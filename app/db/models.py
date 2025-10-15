from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    price: float = 0.0
    tags: str = ""  
    popularity: int = 0

    interactions: List["Interaction"] = Relationship(back_populates="product")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    interactions: List["Interaction"] = Relationship(back_populates="user")

class Interaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    event: str  
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="interactions")
    product: Optional[Product] = Relationship(back_populates="interactions")
