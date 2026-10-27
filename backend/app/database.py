"""
SentinelAI-X Database Module
==============================
SQLAlchemy ORM engine, session lifecycle management, and base declarative class.
Uses SQLite for zero-config embedded persistence with easy portability to PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# For SQLite, check_same_thread needs to be False for FastAPI concurrency
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables and seed initial essential data."""
    import models  # Ensure all models are registered with Base.metadata
    Base.metadata.create_all(bind=engine)
