# database/connection.py
# ----------------------------------------------------------------------
# Database engine setup using SQLAlchemy + SQLite.
# SQLite stores everything in a single file: nexus_ops.db
# Zero configuration required — works on any machine.
# ----------------------------------------------------------------------

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# ── Engine ────────────────────────────────────────────────────────────
# SQLite file lives in the project root
DB_PATH   = os.path.join(os.path.dirname(__file__), "..", "nexus_ops.db")
DB_URL    = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine    = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base class all models inherit from ───────────────────────────────
class Base(DeclarativeBase):
    pass


def get_db():
    """Yields a database session. Use as a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables if they don't exist yet. Call once on startup."""
    from database.models import Incident, AgentTrace   # avoid circular import
    Base.metadata.create_all(bind=engine)
    print("[Database] SQLite tables initialized at:", os.path.abspath(DB_PATH))


# ── PostgreSQL swap (for production) ─────────────────────────────────
# To use PostgreSQL instead of SQLite, replace DB_URL with:
#
# DB_URL = (
#     f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
#     f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
#     f"/{os.getenv('POSTGRES_DB')}"
# )
# and remove connect_args={"check_same_thread": False}