"""Postgres-backed integration tests for the events data path.

The Event model uses a Postgres ARRAY column, which SQLite cannot create, so
these run only when TEST_DATABASE_URL points at a (disposable) Postgres database:

    TEST_DATABASE_URL=postgresql://user@localhost:5432/penguwave_test pytest
"""
import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.core.security import hash_password
from app.main import app
from app.models.event import Event
from app.models.user import ROLE_VIEWER, STATUS_ACTIVE, User

PG_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    PG_URL is None, reason="Set TEST_DATABASE_URL to run Postgres integration tests"
)


@pytest.fixture
def pg_client():
    engine = create_engine(PG_URL)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            User(
                id="u-v",
                email="v@penguwave.io",
                password_hash=hash_password("viewerpass"),
                role=ROLE_VIEWER,
                status=STATUS_ACTIVE,
            )
        )
        session.add(
            Event(
                id="evt-a",
                timestamp=datetime(2025, 2, 18, tzinfo=timezone.utc),
                severity="HIGH",
                title="Event A",
                asset_hostname="host-a",
                asset_ip="10.0.0.1",
                source_ip="10.0.0.2",
                tags=["t1"],
            )
        )
        session.add(
            Event(  # later timestamp + missing optional fields
                id="evt-b",
                timestamp=datetime(2025, 2, 19, tzinfo=timezone.utc),
                severity="LOW",
                title="Event B",
            )
        )
        session.commit()

        app.dependency_overrides[get_session] = lambda: session
        with TestClient(app) as c:
            c.post(
                "/api/auth/login",
                json={"email": "v@penguwave.io", "password": "viewerpass"},
            )
            yield c
        app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


def test_list_events_camelcase_and_sorted_desc(pg_client):
    res = pg_client.get("/api/events")
    assert res.status_code == 200
    data = res.json()
    assert [e["id"] for e in data] == ["evt-b", "evt-a"]  # newest first
    a = next(e for e in data if e["id"] == "evt-a")
    assert a["assetHostname"] == "host-a"
    assert a["sourceIp"] == "10.0.0.2"
    b = next(e for e in data if e["id"] == "evt-b")
    assert b["sourceIp"] is None  # missing field preserved as null
    assert b["tags"] == []


def test_get_event_detail(pg_client):
    res = pg_client.get("/api/events/evt-a")
    assert res.status_code == 200
    assert res.json()["assetIp"] == "10.0.0.1"


def test_get_missing_event_is_404(pg_client):
    res = pg_client.get("/api/events/does-not-exist")
    assert res.status_code == 404
    assert res.json() == {"error": "Event not found"}


def test_events_forbidden_without_login():
    engine = create_engine(PG_URL)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        with TestClient(app) as c:
            assert c.get("/api/events").status_code == 401
        app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
