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


def register_and_login(client, email="new@example.com"):
    client.post(
        "/register",
        data={"name": "New Person", "email": email, "password": "password123"},
    )
    return login(client, email, "password123")


def test_profile_requires_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_profile_shows_demo_data(client):
    login(client)
    resp = client.get("/profile")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "322.24" in html
    assert "Bills" in html
    assert html.count('class="category-badge"') == 8
    assert html.count('class="category-row"') == 7


def test_profile_empty_state_for_new_user(client):
    register_and_login(client)
    resp = client.get("/profile")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "New Person" in html
    assert "₹0.00" in html
    assert "No expenses yet" in html
    assert "322.24" not in html


def test_profile_isolated_between_users(client):
    register_and_login(client)
    html = client.get("/profile").data.decode()
    assert "Weekly groceries" not in html


def test_profile_stale_session_redirects(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 9999
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize("path", ["/", "/login", "/register"])
def test_logged_in_user_redirected_to_profile(client, path):
    login(client)
    resp = client.get(path)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")
