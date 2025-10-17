from sqlmodel import SQLModel, create_engine, Session
from .models import Product, User, Interaction
from typing import Iterator
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./recs.db")

connect_args = {}
if DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DB_URL, 
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True  # verify connections before use
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
