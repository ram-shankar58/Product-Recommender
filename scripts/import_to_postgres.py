"""
Import CSV files from ./data into the configured DATABASE_URL using SQLModel.
If DATABASE_URL is not set, the script will exit with an error explaining how to start the local postgres compose.
"""
import os
import sys
from sqlmodel import SQLModel, create_engine, Session
from app.db.models import Product, User, Interaction
import csv
from pathlib import Path

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("ERROR: DATABASE_URL is not set. Start the local Postgres with: docker compose up -d")
    sys.exit(1)

connect_args = {}
if DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DB_URL, echo=False, connect_args=connect_args)

print("Using DATABASE_URL:", DB_URL)
print("Creating tables...")
SQLModel.metadata.create_all(engine)

root = Path(__file__).parent.parent
data_dir = root / "data"
prod_path = data_dir / "products.csv"
users_path = data_dir / "users.csv"
inter_path = data_dir / "interactions.csv"

with Session(engine) as session:
    created = {"products": 0, "users": 0, "interactions": 0}

    if prod_path.exists():
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
    if users_path.exists():
        with open(users_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                u = User(
                    id=int(row["id"]) if row.get("id") else None,
                    name=row.get("name", "")
                )
                session.add(u)
                created["users"] += 1
    session.commit()
    if inter_path.exists():
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

print("Import complete:", created)
print("You can now set DATABASE_URL to your Postgres and run the backend.")
