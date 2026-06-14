def test_login_success_sets_cookie_and_returns_user_only(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "admin@penguwave.io", "password": "adminpass"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["email"] == "admin@penguwave.io"
    assert body["user"]["role"] == "admin"
    # No token in the body (cookie-only auth); no password leakage.
    assert "token" not in body
    assert "password" not in str(body).lower()
    assert "pw_session" in res.cookies


def test_login_wrong_password_is_401_with_error_shape(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "admin@penguwave.io", "password": "nope"},
    )
    assert res.status_code == 401
    assert res.json() == {"error": "Invalid email or password"}


def test_login_unknown_email_is_401(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "ghost@penguwave.io", "password": "whatever"},
    )
    assert res.status_code == 401


def test_login_disabled_account_is_403(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "off@penguwave.io", "password": "disabledpass"},
    )
    assert res.status_code == 403


def test_login_invalid_email_is_400(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "not-an-email", "password": "x"},
    )
    assert res.status_code == 400
    assert "error" in res.json()


def test_me_requires_authentication(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json() == {"error": "Authentication required"}


def test_me_returns_current_user_after_login(client):
    client.post(
        "/api/auth/login",
        json={"email": "admin@penguwave.io", "password": "adminpass"},
    )
    res = client.get("/api/auth/me")
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "admin@penguwave.io"
    assert body["role"] == "admin"
    assert "password_hash" not in body


def test_logout_clears_session(client):
    client.post(
        "/api/auth/login",
        json={"email": "admin@penguwave.io", "password": "adminpass"},
    )
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.json() == {"message": "Logged out"}
    # After logout the session cookie is gone, so /me is unauthorized again.
    assert client.get("/api/auth/me").status_code == 401
