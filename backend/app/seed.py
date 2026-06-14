"""Seed the database with users and the mock security events.

Seed user credentials come from the environment only (never committed). Run:

    SECRET_KEY=... DATABASE_URL=... \
    SEED_ADMIN_EMAIL=... SEED_ADMIN_PASSWORD=... \
    python -m app.seed

Idempotent: re-running upserts rows by primary key.
"""
import json
from datetime import datetime
from pathlib import Path

from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db
from app.core.security import hash_password
from app.models.event import Event
from app.models.user import ROLE_ADMIN, ROLE_VIEWER, User

SEED_DATA = Path(__file__).resolve().parent.parent / "seed_data" / "mock_events.json"


def _parse_timestamp(value: str) -> datetime:
    # Mock data uses trailing 'Z' (UTC); fromisoformat needs an explicit offset.
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_events(raw: list[dict]) -> list[Event]:
    """Map raw contract-shaped (camelCase) records to Event rows. Drops userId."""
    return [
        Event(
            id=r["id"],
            timestamp=_parse_timestamp(r["timestamp"]),
            severity=r["severity"],
            title=r["title"],
            description=r.get("description"),
            asset_hostname=r.get("assetHostname"),
            asset_ip=r.get("assetIp"),
            source_ip=r.get("sourceIp"),
            tags=r.get("tags", []),
        )
        for r in raw
    ]


def load_events_from_disk() -> list[Event]:
    return build_events(json.loads(SEED_DATA.read_text()))


def build_seed_users() -> list[User]:
    """Build seed users from environment-provided credentials."""
    users: list[User] = []
    if settings.seed_admin_email and settings.seed_admin_password:
        users.append(
            User(
                id="usr-admin",
                email=settings.seed_admin_email,
                password_hash=hash_password(settings.seed_admin_password),
                role=ROLE_ADMIN,
            )
        )
    if settings.seed_viewer_email and settings.seed_viewer_password:
        users.append(
            User(
                id="usr-viewer",
                email=settings.seed_viewer_email,
                password_hash=hash_password(settings.seed_viewer_password),
                role=ROLE_VIEWER,
            )
        )
    if not users:
        raise RuntimeError(
            "No seed users configured. Set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD "
            "(and optionally SEED_VIEWER_*) in the environment."
        )
    return users


def run() -> None:
    init_db()
    users = build_seed_users()
    events = load_events_from_disk()
    with Session(engine) as session:
        for user in users:
            session.merge(user)
        for event in events:
            session.merge(event)
        session.commit()
    print(f"Seeded {len(users)} users and {len(events)} events.")


if __name__ == "__main__":
    run()
