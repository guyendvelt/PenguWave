# Ensure a signing key exists before any app module reads settings.
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-bytes-long-000")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.core.security import hash_password
from app.main import app
from app.models.user import (
    ROLE_ADMIN,
    ROLE_VIEWER,
    STATUS_ACTIVE,
    STATUS_DISABLED,
    User,
)


@pytest.fixture
def session():
    """In-memory SQLite session with only the User table (avoids Postgres ARRAY)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine, tables=[User.__table__])
    with Session(engine) as s:
        s.add(
            User(
                id="u-admin",
                email="admin@penguwave.io",
                password_hash=hash_password("adminpass"),
                role=ROLE_ADMIN,
                status=STATUS_ACTIVE,
            )
        )
        s.add(
            User(
                id="u-viewer",
                email="viewer@penguwave.io",
                password_hash=hash_password("viewerpass"),
                role=ROLE_VIEWER,
                status=STATUS_ACTIVE,
            )
        )
        s.add(
            User(
                id="u-disabled",
                email="off@penguwave.io",
                password_hash=hash_password("disabledpass"),
                status=STATUS_DISABLED,
            )
        )
        s.commit()
        yield s


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
