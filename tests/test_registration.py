import pytest
from werkzeug.security import check_password_hash

import app as app_module
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def user_count():
    conn = db.get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def post(client, name="Ada", email="ada@example.com", password="password123"):
    return client.post(
        "/register", data={"name": name, "email": email, "password": password}
    )


def test_get_register(client):
    assert client.get("/register").status_code == 200


def test_valid_registration(client):
    resp = post(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    user = db.get_user_by_email("ada@example.com")
    assert user is not None
    assert user["password_hash"] != "password123"
    assert check_password_hash(user["password_hash"], "password123")


def test_duplicate_email_case_insensitive(client):
    post(client)
    resp = post(client, email="ADA@example.com")
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert user_count() == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "   "},
        {"email": "a"},
        {"email": "@x.com"},
        {"email": "a@"},
        {"password": "short"},
    ],
)
def test_invalid_input_creates_no_user(client, kwargs):
    resp = post(client, **kwargs)
    assert resp.status_code == 200
    assert b"auth-error" in resp.data
    assert user_count() == 0


def test_failed_submit_keeps_fields_not_password(client):
    resp = post(client, name="Ada", email="ada@example.com", password="short")
    assert b'value="Ada"' in resp.data
    assert b'value="ada@example.com"' in resp.data
    assert b"short" not in resp.data.replace(b"Password must be", b"")


def test_seeded_demo_user_unaffected(client):
    db.seed_db()
    post(client)
    assert db.get_user_by_email("demo@spendly.com") is not None
    assert user_count() == 2
