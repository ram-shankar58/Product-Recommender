from typing import List, Dict, Optional
from sqlmodel import Session, select
from ..db.models import Product, Interaction

# Simple tag-based recommender with popularity boost.

def recommend_for_user(session: Session, user_id: int, k: int = 5) -> List[Product]:
    # Collect user tag preferences from their interactions
    interactions = session.exec(
        select(Interaction).where(Interaction.user_id == user_id)
    ).all()

    liked_tags: Dict[str, int] = {}
    for inter in interactions:
        # weight events
        weight = 1
        if inter.event == "view":
            weight = 1
        elif inter.event == "add_to_cart":
            weight = 3
        elif inter.event == "purchase":
            weight = 5
        product = session.get(Product, inter.product_id)
        if not product:
            continue
        for t in [t.strip().lower() for t in product.tags.split(",") if t.strip()]:
            liked_tags[t] = liked_tags.get(t, 0) + weight

    # Score all products by tag overlap + popularity
    products = session.exec(select(Product)).all()
    scored = []
    for p in products:
        p_tags = [t.strip().lower() for t in p.tags.split(",") if t.strip()]
        tag_score = sum(liked_tags.get(t, 0) for t in p_tags)
        popularity_boost = min(p.popularity, 10)  # small cap
        score = tag_score + 0.5 * popularity_boost
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:k]]


def recommend_from_behavior(
    session: Session,
    product_ids: Optional[List[int]] = None,
    tags: Optional[List[str]] = None,
    k: int = 5,
) -> List[Product]:
    liked_tags: Dict[str, int] = {}
    tags = [t.strip().lower() for t in (tags or []) if t.strip()]

    # derive from product ids
    for pid in product_ids or []:
        p = session.get(Product, pid)
        if not p:
            continue
        for t in [t.strip().lower() for t in p.tags.split(",") if t.strip()]:
            liked_tags[t] = liked_tags.get(t, 0) + 2

    # incorporate explicit tags
    for t in tags:
        liked_tags[t] = liked_tags.get(t, 0) + 3

    products = session.exec(select(Product)).all()
    scored = []
    for p in products:
        p_tags = [t.strip().lower() for t in p.tags.split(",") if t.strip()]
        tag_score = sum(liked_tags.get(t, 0) for t in p_tags)
        popularity_boost = min(p.popularity, 10)
        score = tag_score + 0.5 * popularity_boost
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:k]]
