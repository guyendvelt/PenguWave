def _login(client, email, password):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_users_list_requires_auth(client):
    assert client.get("/api/users").status_code == 401


def test_users_list_forbidden_for_viewer(client):
    _login(client, "viewer@penguwave.io", "viewerpass")
    res = client.get("/api/users")
    assert res.status_code == 403
    assert res.json() == {"error": "Forbidden"}


def test_admin_lists_users_without_passwords(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.get("/api/users")
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 3
    assert all("password" not in str(u).lower() for u in users)


def test_admin_creates_user(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.post(
        "/api/users",
        json={"email": "new@penguwave.io", "password": "strongpass", "role": "viewer"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "new@penguwave.io"
    assert body["role"] == "viewer"
    assert body["id"].startswith("usr-")
    assert "password" not in str(body).lower()


def test_create_duplicate_email_is_400(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.post(
        "/api/users",
        json={"email": "admin@penguwave.io", "password": "strongpass", "role": "viewer"},
    )
    assert res.status_code == 400


def test_create_invalid_role_is_400(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.post(
        "/api/users",
        json={"email": "x@penguwave.io", "password": "strongpass", "role": "superuser"},
    )
    assert res.status_code == 400


def test_create_short_password_is_400(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.post(
        "/api/users",
        json={"email": "x@penguwave.io", "password": "short", "role": "viewer"},
    )
    assert res.status_code == 400


def test_patch_updates_role_and_status(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.patch(
        "/api/users/u-viewer", json={"role": "admin", "status": "disabled"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["role"] == "admin"
    assert body["status"] == "disabled"


def test_patch_invalid_status_is_400(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.patch("/api/users/u-viewer", json={"status": "banished"})
    assert res.status_code == 400


def test_patch_missing_user_is_404(client):
    _login(client, "admin@penguwave.io", "adminpass")
    assert client.patch("/api/users/nope", json={"role": "viewer"}).status_code == 404


def test_delete_other_user(client):
    _login(client, "admin@penguwave.io", "adminpass")
    res = client.delete("/api/users/u-viewer")
    assert res.status_code == 200
    assert res.json() == {"message": "User deleted"}


def test_delete_self_is_blocked(client):
    _login(client, "admin@penguwave.io", "adminpass")
    assert client.delete("/api/users/u-admin").status_code == 400


def test_delete_missing_user_is_404(client):
    _login(client, "admin@penguwave.io", "adminpass")
    assert client.delete("/api/users/nope").status_code == 404
