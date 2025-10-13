from sqlmodel import SQLModel, create_engine, Session
from .models import Product, User, Interaction
from typing import Iterator
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./recs.db")
engine = create_engine(DB_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
