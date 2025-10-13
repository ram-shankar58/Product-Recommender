from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
app=FastAPI()

users=[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

products = [
    {"id": 1, "name": "Noise Cancelling Headphones", "category": "Audio"},
    {"id": 2, "name": "Bluetooth Speaker", "category": "Audio"},
    {"id": 3, "name": "Smart Watch", "category": "Wearable"},
]

# Sample user interactions (User 1 viewed product 1, User 2 viewed product 2)

interactions = [
    {"user_id": 1, "product_id": 1, "action": "view"},
    {"user_id": 2, "product_id": 2, "action": "view"},
    {"user_id": 1, "product_id": 3, "action": "view"},
]

class Recommendation(BaseModel):
    product_id:int
    product_name: str
    explanation: str


def recommend_products_for_user(user_id:int, top_n=1) -> List[dict]:
    user_product_ids=[i[product_id] for i in interactions if i['user_id' \
    ']==user_id']]