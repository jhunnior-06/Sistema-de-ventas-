import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def get_database_url() -> str | None:
    """Obtiene la conexión creada por Neon o una variable configurada manualmente."""
    variable_names = (
        "DATABASE_URL",
        "POSTGRES_URL",
        "DATABASE_POSTGRES_URL",
        "DATABASE_URL_UNPOOLED",
        "DATABASE_URL_NON_POOLING",
    )
    return next((os.getenv(name) for name in variable_names if os.getenv(name)), None)


DATABASE_URL = get_database_url()

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Neon entrega esta variante; SQLAlchemy usará psycopg v3.
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    if os.getenv("VERCEL"):
        raise RuntimeError(
            "Conecta Neon en Vercel o configura DATABASE_URL para PostgreSQL."
        )
    DATABASE_URL = "sqlite:///./ventas.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # Registra los modelos antes de crear las tablas.

    Base.metadata.create_all(bind=engine)
