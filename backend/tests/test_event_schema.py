from datetime import datetime, timezone

from app.models.event import Event
from app.schemas.event import EventPublic


def test_event_public_serializes_camelcase_aliases():
    e = Event(
        id="evt-1",
        timestamp=datetime(2025, 2, 18, 14, 32, 1, tzinfo=timezone.utc),
        severity="HIGH",
        title="t",
        description=None,
        asset_hostname="host-1",
        asset_ip="10.0.0.1",
        source_ip=None,
        tags=["x"],
    )
    data = EventPublic.model_validate(e).model_dump(by_alias=True)
    assert data["assetHostname"] == "host-1"
    assert data["assetIp"] == "10.0.0.1"
    assert data["sourceIp"] is None
    assert data["tags"] == ["x"]
    # snake_case keys must not leak into the API representation.
    assert "asset_hostname" not in data
    assert "source_ip" not in data
