from datetime import date

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


def day(n):
    return date.today().replace(day=n).isoformat()


def test_unfiltered_profile_unchanged(client):
    login(client)
    html = client.get("/profile").data.decode()
    assert "322.24" in html
    assert html.count('class="category-badge"') == 8


def test_range_filters_everything(client):
    login(client)
    html = client.get(f"/profile?from={day(10)}&to={day(18)}").data.decode()
    # Bills 120 + Health 35.75 + Entertainment 18
    assert "173.75" in html
    assert html.count('class="category-badge"') == 3
    assert "322.24" not in html


def test_open_ended_ranges(client):
    login(client)
    data = client.get(f"/profile/data?from={day(22)}").get_json()
    assert data["summary"]["count"] == 2
    data = client.get(f"/profile/data?to={day(1)}").get_json()
    assert data["summary"]["count"] == 1


@pytest.mark.parametrize(
    "qs", ["from=garbage", "to=2026-13-45", f"from={day(20)}&to={day(1)}"]
)
def test_bad_ranges_do_not_500(client, qs):
    login(client)
    resp = client.get(f"/profile?{qs}")
    assert resp.status_code == 200
    assert 'role="alert"' in resp.data.decode()


def test_reversed_range_is_ignored(client):
    login(client)
    html = client.get(f"/profile?from={day(20)}&to={day(1)}").data.decode()
    assert "322.24" in html


def test_empty_range(client):
    login(client)
    html = client.get("/profile?from=1999-01-01&to=1999-01-31").data.decode()
    assert "₹0.00" in html
    assert "No expenses in this range" in html


def test_filter_form_repopulates(client):
    login(client)
    html = client.get(f"/profile?from={day(2)}&to={day(9)}").data.decode()
    assert f'value="{day(2)}"' in html
    assert f'value="{day(9)}"' in html


def test_json_matches_page(client):
    login(client)
    data = client.get("/profile/data").get_json()
    assert set(data) == {"summary", "categories", "recent"}
    assert data["summary"] == {
        "total": 322.24, "count": 8, "top_category": "Bills"
    }
    assert len(data["categories"]) == 7
    assert len(data["recent"]) == 8
    assert "password_hash" not in str(data)


def test_json_requires_login(client):
    resp = client.get("/profile/data")
    assert resp.status_code == 401
    assert resp.get_json() == {"error": "Not logged in"}
    assert client.get("/profile").status_code == 302


def test_isolation_on_json(client):
    client.post(
        "/register",
        data={"name": "Other", "email": "o@example.com", "password": "password123"},
    )
    login(client, "o@example.com", "password123")
    data = client.get("/profile/data").get_json()
    assert data["summary"]["count"] == 0
    assert data["recent"] == []
