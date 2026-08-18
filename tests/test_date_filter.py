from datetime import date, datetime, timedelta

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
def authed_client(client, seed_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_id
    return client


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def this_month_range(today):
    first = today.replace(day=1)
    return first.isoformat(), today.isoformat()


@pytest.fixture
def empty_range():
    last_month_end = date.today().replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start.isoformat(), last_month_end.isoformat()


# ------------------------------------------------------------------ #
# Unit tests — get_summary_stats with date range                     #
# ------------------------------------------------------------------ #

def test_summary_stats_current_month_matches_unfiltered(seed_id, this_month_range):
    df, dt = this_month_range
    filtered = queries.get_summary_stats(seed_id, df, dt)
    unfiltered = queries.get_summary_stats(seed_id)
    assert filtered == unfiltered
    assert filtered["total_spent"] == 346.24
    assert filtered["transaction_count"] == 8
    assert filtered["top_category"] == "Bills"


def test_summary_stats_empty_range(seed_id, empty_range):
    df, dt = empty_range
    assert queries.get_summary_stats(seed_id, df, dt) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


def test_summary_stats_none_range_unchanged(seed_id):
    assert queries.get_summary_stats(seed_id, None, None) == queries.get_summary_stats(seed_id)


# ------------------------------------------------------------------ #
# Unit tests — get_recent_transactions with date range               #
# ------------------------------------------------------------------ #

def test_recent_transactions_current_month(seed_id, this_month_range):
    df, dt = this_month_range
    txns = queries.get_recent_transactions(seed_id, date_from=df, date_to=dt)
    assert len(txns) == 8
    dates = [t["date"] for t in txns]
    assert dates == sorted(dates, reverse=True)


def test_recent_transactions_empty_range(seed_id, empty_range):
    df, dt = empty_range
    assert queries.get_recent_transactions(seed_id, date_from=df, date_to=dt) == []


def test_recent_transactions_limit_with_range(seed_id, this_month_range):
    df, dt = this_month_range
    txns = queries.get_recent_transactions(seed_id, limit=3, date_from=df, date_to=dt)
    assert len(txns) == 3


# ------------------------------------------------------------------ #
# Unit tests — get_category_breakdown with date range                #
# ------------------------------------------------------------------ #

def test_category_breakdown_current_month(seed_id, this_month_range):
    df, dt = this_month_range
    cats = queries.get_category_breakdown(seed_id, df, dt)
    assert len(cats) == 7
    assert sum(c["pct"] for c in cats) == 100


def test_category_breakdown_empty_range(seed_id, empty_range):
    df, dt = empty_range
    assert queries.get_category_breakdown(seed_id, df, dt) == []


# ------------------------------------------------------------------ #
# Route tests — /profile with and without filters                    #
# ------------------------------------------------------------------ #

def test_profile_no_params_unfiltered_and_all_time_active(authed_client):
    resp = authed_client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨346.24" in body
    assert ">8<" in body
    assert "Bills" in body
    assert 'class="preset-btn is-active" href="/profile"' in body


def test_profile_this_month_preset(authed_client, this_month_range):
    df, dt = this_month_range
    resp = authed_client.get(f"/profile?date_from={df}&date_to={dt}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨346.24" in body
    assert ">8<" in body
    assert 'This Month</a>' in body
    assert 'class="preset-btn is-active" href="/profile?date_from=' in body


def test_profile_custom_range_valid(authed_client, this_month_range):
    df, dt = this_month_range
    resp = authed_client.get(f"/profile?date_from={df}&date_to={dt}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert f'name="date_from" value="{df}"' in body
    assert f'name="date_to" value="{dt}"' in body


def test_profile_custom_range_empty(authed_client, empty_range):
    df, dt = empty_range
    resp = authed_client.get(f"/profile?date_from={df}&date_to={dt}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨0.00" in body
    assert ">0<" in body
    assert ">—<" in body


def test_profile_reversed_dates_flashes_error(authed_client, today):
    df = (today + timedelta(days=10)).isoformat()
    dt = today.isoformat()
    resp = authed_client.get(f"/profile?date_from={df}&date_to={dt}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Start date must be before end date." in body
    assert "₨346.24" in body
    assert ">8<" in body


def test_profile_malformed_date_no_crash(authed_client):
    resp = authed_client.get("/profile?date_from=not-a-date")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨346.24" in body


def test_profile_partial_param_unfiltered(authed_client):
    resp = authed_client.get("/profile?date_from=2026-01-01")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨346.24" in body
    assert ">8<" in body


def test_profile_empty_range_no_errors(authed_client, empty_range):
    df, dt = empty_range
    resp = authed_client.get(f"/profile?date_from={df}&date_to={dt}")
    body = resp.get_data(as_text=True)
    assert "₨0.00" in body
    assert ">0<" in body
    assert ">—<" in body
    assert "Traceback" not in body
