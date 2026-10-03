import pytest

import app as app_module
from database import db

DEMO = {"email": "demo@spendly.com", "password": "demo123"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def login(client, email=DEMO["email"], password=DEMO["password"]):
    return client.post("/login", data={"email": email, "password": password})


def session_data(client):
    with client.session_transaction() as sess:
        return dict(sess)


def test_get_login(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Sign in" in resp.data


def test_demo_login_sets_only_user_id(client):
    resp = login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")
    user = db.get_user_by_email(DEMO["email"])
    assert session_data(client) == {"user_id": user["id"]}


def test_email_is_case_and_whitespace_insensitive(client):
    resp = login(client, email="  DEMO@Spendly.com ")
    assert resp.status_code == 302
    assert "user_id" in session_data(client)


def test_wrong_password_and_unknown_email_share_error(client):
    bad_pw = login(client, password="wrong-password")
    unknown = login(client, email="nobody@example.com")
    for resp in (bad_pw, unknown):
        assert resp.status_code == 200
        assert b"Invalid email or password." in resp.data
        assert "user_id" not in session_data(client)


def test_failed_submit_keeps_email_not_password(client):
    resp = login(client, password="wrong-password")
    assert b'value="demo@spendly.com"' in resp.data
    assert b"wrong-password" not in resp.data


def test_registered_user_can_log_in(client):
    client.post(
        "/register",
        data={"name": "Ada", "email": "ada@example.com", "password": "password123"},
    )
    resp = login(client, email="ada@example.com", password="password123")
    assert resp.status_code == 302
    assert "user_id" in session_data(client)


def test_navbar_reflects_auth_state(client):
    out = client.get("/").data
    assert b"Sign in" in out and b"Get started" in out
    assert b"Log out" not in out

    login(client)
    inn = client.get("/terms").data
    assert b"Log out" in inn
    assert b"Get started" not in inn and b"Sign in" not in inn


@pytest.mark.parametrize("path", ["/login", "/register"])
def test_logged_in_users_are_redirected_to_profile(client, path):
    login(client)
    resp = client.get(path)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_logout_clears_session(client):
    login(client)
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")
    assert "user_id" not in session_data(client)


def test_logout_when_logged_out(client):
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")
