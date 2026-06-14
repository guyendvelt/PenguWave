"""Auth-gating for event endpoints (runs on the SQLite client fixture — the 401
path short-circuits before any DB query). Data-returning behavior is covered by
the Postgres integration tests in test_integration_pg.py."""


def test_events_list_requires_auth(client):
    res = client.get("/api/events")
    assert res.status_code == 401
    assert res.json() == {"error": "Authentication required"}


def test_event_detail_requires_auth(client):
    assert client.get("/api/events/evt-001").status_code == 401
