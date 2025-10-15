from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional
from .db.database import init_db, get_session
from .db.models import Product, User, Interaction
from .recs.engine import recommend_for_user, recommend_from_behavior
from sqlmodel import Session, select
import asyncio
from .llm.explainer import explain
from dotenv import load_dotenv
import os
import csv

app = FastAPI(title="Product Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    init_db()

class Behavior(BaseModel):
    product_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None

class RecRequest(BaseModel):
    user_id: Optional[int] = None
    user_behavior: Optional[Behavior] = None
    k: int = 5

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    tags: List[str]
    explanation: str

@app.post("/load-sample-data")
def load_sample_data(session: Session = Depends(get_session)):
    # ensure tables exist in case startup event didn't run
    init_db()
    # simple guard: only load if empty
    if session.exec(select(Product)).first():
        return {"status": "already-loaded"}

    products = [
        Product(name="Trail Running Shoes", description="Cushioned trail shoes", price=129.0, tags="running,trail,shoes", popularity=8),
        Product(name="Road Running Shoes", description="Lightweight road shoes", price=119.0, tags="running,road,shoes", popularity=9),
        Product(name="Yoga Mat", description="Non-slip yoga mat", price=39.0, tags="yoga,fitness,mat", popularity=7),
        Product(name="Dumbbell Set", description="Adjustable dumbbells", price=199.0, tags="strength,fitness,weights", popularity=6),
        Product(name="Hiking Backpack", description="30L daypack", price=89.0, tags="hiking,trail,backpack", popularity=8),
        Product(name="Noise Cancelling Headphones", description="Over-ear ANC", price=249.0, tags="audio,electronics,headphones", popularity=10),
    ]
    for p in products:
        session.add(p)
    users = [User(name="Alice"), User(name="Bob")]
    for u in users:
        session.add(u)
    session.commit()

    alice_id = users[0].id
    bob_id = users[1].id
    all_products = session.exec(select(Product)).all()
    name_to_id = {p.name: p.id for p in all_products}

    interactions = [
        Interaction(user_id=alice_id, product_id=name_to_id["Trail Running Shoes"], event="view"),
        Interaction(user_id=alice_id, product_id=name_to_id["Road Running Shoes"], event="add_to_cart"),
        Interaction(user_id=alice_id, product_id=name_to_id["Yoga Mat"], event="purchase"),
        Interaction(user_id=bob_id, product_id=name_to_id["Hiking Backpack"], event="view"),
        Interaction(user_id=bob_id, product_id=name_to_id["Noise Cancelling Headphones"], event="purchase"),
    ]
    for it in interactions:
        session.add(it)
    session.commit()

    return {"status": "loaded", "users": [u.id for u in users], "products": [p.id for p in products]}

@app.post("/recommendations", response_model=List[ProductOut])
async def recommendations(req: RecRequest, session: Session = Depends(get_session)):
    init_db()
    if req.user_id is None and req.user_behavior is None:
        return []

    if req.user_id is not None:
        products = recommend_for_user(session, req.user_id, req.k)
        signals = f"past interactions and similar tags"
    else:
        pb = req.user_behavior
        products = recommend_from_behavior(session, pb.product_ids, pb.tags, req.k)
        sig_parts = []
        if pb.product_ids:
            sig_parts.append(f"similar to items you viewed/bought: {pb.product_ids}")
        if pb.tags:
            sig_parts.append(f"aligned with interests: {', '.join(pb.tags)}")
        signals = "; ".join(sig_parts) or "your interests"

    tasks = [explain(p.name, signals) for p in products]
    explanations = await asyncio.gather(*tasks)

    result: List[ProductOut] = []
    for p, exp in zip(products, explanations):
        result.append(
            ProductOut(
                id=p.id,
                name=p.name,
                price=p.price,
                tags=[t.strip() for t in p.tags.split(',') if t.strip()],
                explanation=exp,
            )
        )
    return result


@app.get("/")
def root():
    return {"status": "ok", "demo": "/demo", "api_docs": "/docs"}


@app.get("/data-info")
def data_info(session: Session = Depends(get_session)):
    """Get information about currently loaded data."""
    from sqlmodel import func
    
    product_count = session.exec(select(func.count(Product.id))).one()
    user_count = session.exec(select(func.count(User.id))).one()
    interaction_count = session.exec(select(func.count(Interaction.id))).one()
    
    sample_products = session.exec(select(Product).limit(3)).all()
    product_names = [p.name for p in sample_products]
    
    # Heuristic detection
    data_source = "unknown"
    if any("Essence" in name or "iPhone" in name or "Samsung" in name for name in product_names):
        data_source = "api_real_products"
        description = "Real products from DummyJSON/FakeStore APIs"
    elif any("Trail Running" in name or "Yoga Mat" in name for name in product_names):
        data_source = "synthetic_realistic"
        description = "Generated realistic e-commerce data"
    elif any("brazilian" in str(sample_products).lower()):
        data_source = "kaggle_brazilian"
        description = "Kaggle Brazilian E-Commerce dataset"
    else:
        data_source = "custom"
        description = "Custom or manually loaded data"
    
    return {
        "source": data_source,
        "description": description,
        "stats": {
            "products": product_count,
            "users": user_count,
            "interactions": interaction_count
        },
        "sample_products": product_names[:3]
    }



static_dir = os.path.join(os.path.dirname(__file__), "static")
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
if os.path.isdir(static_dir):
    app.mount("/demo", StaticFiles(directory=static_dir, html=True), name="demo")
if os.path.isdir(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")

@app.get("/active-users")
def active_users(session: Session = Depends(get_session)):
    user_ids = set()
    for row in session.exec(select(Interaction.user_id)).all():
        user_ids.add(row)
    users = session.exec(select(User).where(User.id.in_(user_ids))).all()
    return [{"id": u.id, "name": u.name} for u in users]


@app.post("/load-data-source")
def load_data_source(source: str, session: Session = Depends(get_session)):
    """
    Load data from a specific source.
    Sources: 'api', 'synthetic', 'sample'
    """
    import subprocess
    import sys
    
    session.exec(select(Interaction)).all()
    for item in session.exec(select(Interaction)):
        session.delete(item)
    for item in session.exec(select(Product)):
        session.delete(item)
    for item in session.exec(select(User)):
        session.delete(item)
    session.commit()
    
    script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
    
    try:
        if source == "api":
            result = subprocess.run(
                [sys.executable, os.path.join(script_dir, "fetch_real_products.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}
            
        elif source == "synthetic":
            result = subprocess.run(
                [sys.executable, os.path.join(script_dir, "generate_realistic_data.py")],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}
            
        elif source == "sample":
            return load_sample_data(session)
        
        else:
            return {"status": "error", "message": f"Unknown source: {source}"}
        
        import_result = import_csv(session)
        
        return {
            "status": "success",
            "source": source,
            "import_result": import_result
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
def import_csv(session: Session = Depends(get_session)):
    """Import products, users, and interactions from CSV files in ./data.
    Files: data/products.csv, data/users.csv, data/interactions.csv
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(root, "data")
    prod_path = os.path.join(data_dir, "products.csv")
    users_path = os.path.join(data_dir, "users.csv")
    inter_path = os.path.join(data_dir, "interactions.csv")

    created = {"products": 0, "users": 0, "interactions": 0}

    if os.path.exists(prod_path):
        with open(prod_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                p = Product(
                    id=int(row["id"]) if row.get("id") else None,
                    name=row.get("name", ""),
                    description=row.get("description", ""),
                    price=float(row.get("price", 0) or 0),
                    tags=row.get("tags", ""),
                    popularity=int(row.get("popularity", 0) or 0),
                )
                session.add(p)
                created["products"] += 1

    if os.path.exists(users_path):
        with open(users_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                u = User(
                    id=int(row["id"]) if row.get("id") else None,
                    name=row.get("name", "")
                )
                session.add(u)
                created["users"] += 1

    session.commit()

    if os.path.exists(inter_path):
        with open(inter_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                it = Interaction(
                    id=int(row["id"]) if row.get("id") else None,
                    user_id=int(row.get("user_id")),
                    product_id=int(row.get("product_id")),
                    event=row.get("event", "view"),
                )
                session.add(it)
                created["interactions"] += 1
        session.commit()

    return {"status": "imported", **created}


@app.get("/favicon.ico")
def favicon():
    # Serve favicon if present, otherwise return 204 to avoid 404 spam in logs
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    icon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/x-icon")
    return Response(status_code=204)
