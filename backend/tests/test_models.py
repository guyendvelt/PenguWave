from datetime import datetime

from app.models.event import Event
from app.models.user import ROLE_VIEWER, STATUS_ACTIVE, User


def test_user_defaults_to_viewer_and_active():
    u = User(id="usr-001", email="a@penguwave.io", password_hash="hashed")
    assert u.role == ROLE_VIEWER
    assert u.status == STATUS_ACTIVE


def test_user_keeps_string_id():
    u = User(id="usr-002", email="b@penguwave.io", password_hash="hashed", role="admin")
    assert u.id == "usr-002"
    assert u.role == "admin"


def test_event_construction_and_tags():
    e = Event(
        id="evt-001",
        timestamp=datetime(2025, 2, 18, 14, 32, 1),
        severity="HIGH",
        title="Suspicious process",
        description="...",
        asset_hostname="prod-web-03",
        asset_ip="10.0.3.15",
        source_ip="10.0.5.22",
        tags=["endpoint", "mimikatz"],
    )
    assert e.id == "evt-001"
    assert e.tags == ["endpoint", "mimikatz"]
    # userId must not exist on the model.
    assert not hasattr(e, "userId")
    assert not hasattr(e, "user_id")


def test_event_tags_default_empty():
    e = Event(
        id="evt-002",
        timestamp=datetime(2025, 2, 18, 9, 15, 44),
        severity="LOW",
        title="t",
        description="d",
        asset_hostname="h",
        asset_ip="10.0.0.1",
        source_ip="10.0.0.2",
    )
    assert e.tags == []
