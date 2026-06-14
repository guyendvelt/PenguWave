from datetime import datetime, timezone

import pytest

from app.core import config
from app.seed import build_events, build_seed_users, load_events_from_disk


def test_build_events_maps_camelcase_and_drops_userid():
    raw = [
        {
            "id": "evt-1",
            "timestamp": "2025-02-18T14:32:01Z",
            "severity": "HIGH",
            "title": "t",
            "description": "d",
            "assetHostname": "host-1",
            "assetIp": "10.0.0.1",
            "sourceIp": "10.0.0.2",
            "tags": ["a", "b"],
            "userId": "usr-2",
        }
    ]
    event = build_events(raw)[0]
    assert event.asset_hostname == "host-1"
    assert event.asset_ip == "10.0.0.1"
    assert event.source_ip == "10.0.0.2"
    assert event.tags == ["a", "b"]
    assert event.timestamp == datetime(2025, 2, 18, 14, 32, 1, tzinfo=timezone.utc)
    assert not hasattr(event, "userId")
    assert not hasattr(event, "user_id")


def test_build_events_preserves_records_with_missing_fields():
    raw = [
        {
            "id": "evt-058",
            "timestamp": "2025-02-11T15:05:44Z",
            "severity": "HIGH",
            "title": "Orphaned alert",
            # description, assetIp, sourceIp intentionally absent
            "assetHostname": "legacy-ids-02",
            "tags": ["anomaly"],
        }
    ]
    event = build_events(raw)[0]
    assert event.id == "evt-058"
    assert event.source_ip is None
    assert event.asset_ip is None
    assert event.description is None
    assert event.asset_hostname == "legacy-ids-02"


def test_load_events_from_disk_reads_all_mock_events():
    events = load_events_from_disk()
    assert len(events) == 59
    assert all(e.id for e in events)


def test_build_seed_users_requires_env(monkeypatch):
    for attr in (
        "seed_admin_email",
        "seed_admin_password",
        "seed_viewer_email",
        "seed_viewer_password",
    ):
        monkeypatch.setattr(config.settings, attr, None)
    with pytest.raises(RuntimeError):
        build_seed_users()


def test_build_seed_users_hashes_password(monkeypatch):
    monkeypatch.setattr(config.settings, "seed_admin_email", "admin@x.io")
    monkeypatch.setattr(config.settings, "seed_admin_password", "plain-pw")
    monkeypatch.setattr(config.settings, "seed_viewer_email", None)
    monkeypatch.setattr(config.settings, "seed_viewer_password", None)
    users = build_seed_users()
    assert len(users) == 1
    assert users[0].role == "admin"
    assert users[0].password_hash != "plain-pw"
