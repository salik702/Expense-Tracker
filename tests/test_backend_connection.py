from datetime import datetime

import pytest

import database.db as db
from app import app as flask_app
from database import queries


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    flask_app.config["TESTING"] = True
    db.init_db()
    db.seed_db()
    return flask_app


@pytest.fixture
def seed_id(app):
    conn = db.get_db()
    row = conn.execute(
        "SELECT id FROM users WHERE email = 'demo@spendly.com'"
    ).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def empty_user_id(app):
    conn = db.get_db()
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES "
        "('Empty User', 'empty@spendly.com', 'x')"
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


@pytest.fixture
def authed_client(client, seed_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_id
    return client


@pytest.fixture
def authed_empty_client(client, empty_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = empty_user_id
    return client


# ------------------------------------------------------------------ #
# Unit tests — get_user_by_id                                        #
# ------------------------------------------------------------------ #

def test_get_user_by_id_valid(seed_id):
    user = queries.get_user_by_id(seed_id)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert datetime.strptime(user["member_since"], "%B %Y")


def test_get_user_by_id_missing_returns_none():
    assert queries.get_user_by_id(999999) is None


# ------------------------------------------------------------------ #
# Unit tests — get_summary_stats                                     #
# ------------------------------------------------------------------ #

def test_get_summary_stats_with_expenses(seed_id):
    stats = queries.get_summary_stats(seed_id)
    assert stats["total_spent"] == 346.24
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(empty_user_id):
    assert queries.get_summary_stats(empty_user_id) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


# ------------------------------------------------------------------ #
# Unit tests — get_recent_transactions                               #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_ordered(seed_id):
    txns = queries.get_recent_transactions(seed_id)
    assert len(txns) == 8
    dates = [t["date"] for t in txns]
    assert dates == sorted(dates, reverse=True)
    for t in txns:
        assert set(t.keys()) == {"id", "date", "description", "category", "amount"}


def test_get_recent_transactions_no_expenses(empty_user_id):
    assert queries.get_recent_transactions(empty_user_id) == []


# ------------------------------------------------------------------ #
# Unit tests — get_category_breakdown                                #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_ordered_and_pct(seed_id):
    cats = queries.get_category_breakdown(seed_id)
    assert len(cats) == 7
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True)
    pcts = [c["pct"] for c in cats]
    assert all(isinstance(p, int) for p in pcts)
    assert sum(pcts) == 100


def test_get_category_breakdown_no_expenses(empty_user_id):
    assert queries.get_category_breakdown(empty_user_id) == []


# ------------------------------------------------------------------ #
# Route tests — /profile                                             #
# ------------------------------------------------------------------ #

def test_profile_redirects_when_logged_out(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_profile_shows_seed_user(authed_client, seed_id):
    resp = authed_client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₨" in body
    assert "₨346.24" in body
    assert ">8<" in body
    assert "Bills" in body

    for cat in ("Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"):
        assert f">{cat}<" in body

    conn = db.get_db()
    dates = [
        r["date"]
        for r in conn.execute(
            "SELECT date FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
            (seed_id,),
        ).fetchall()
    ]
    conn.close()
    fmt = [datetime.strptime(d, "%Y-%m-%d").strftime("%b %d, %Y") for d in dates]
    assert body.index(fmt[0]) < body.index(fmt[-1])


def test_profile_new_user_empty(authed_empty_client):
    resp = authed_empty_client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨0.00" in body
    assert ">0<" in body
    assert ">—<" in body
    assert ">Food<" not in body


def test_profile_after_register(client):
    resp = client.post(
        "/register",
        data={
            "name": "New User",
            "email": "new@spendly.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "New User" in body
    assert "₨0.00" in body
    assert ">0<" in body
