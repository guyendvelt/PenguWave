"""Database engine and session management.

Uses SQLModel over a local PostgreSQL database (ADR-2 / ADR-6). The engine is
created lazily — importing this module does not open a connection, so the app
and tests can import it without a running database.
"""
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    """Create all tables. Call from a seed script or startup, not at import time."""
    # Import models so they register on SQLModel.metadata before create_all.
    from app.models import event, user  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
