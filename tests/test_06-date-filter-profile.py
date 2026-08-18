"""Tests for the Step 6 date-filter feature on the /profile page.

Spec source of truth: .opencode/specs/06-date-filter-profile.md

Covers:
- /profile with no query params behaving identically to the Step 5 unfiltered view
- "This Month", "Last 3 Months", "Last 6 Months" presets filtering all three
  data sections (summary stats, recent transactions, category breakdown)
- "All Time" clearing any active filter via a clean /profile URL
- Custom date_from/date_to ranges filtering all three sections
- date_from > date_to showing the flash error and falling back to unfiltered
- Malformed and partial date params silently falling back to unfiltered
- Visual indication of the active preset / custom range
- The ₨ (U+20A8) symbol rendering under every filter state
- Empty ranges rendering ₨0.00 / 0 transactions / an empty breakdown, no errors
- Query helper unit tests for get_summary_stats / get_recent_transactions /
  get_category_breakdown with date-range args
- Auth guard: unauthenticated /profile redirects to /login with query params

Fixture conventions follow tests/test_backend_connection.py.
"""

import html
import re
from datetime import date

import pytest
from flask import url_for

import database.db as db
from app import app as flask_app
from database import queries


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _last_day(year, month):
    """Number of days in a given (year, month)."""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - date(year, month, 1)).days


def _shift_months(d, months):
    """The date `months` before/after `d`, clamped to the target month's length.

    Used only to place expense dates outside the window a preset is expected
    to cover (e.g. 4 months ago for a 3-month preset, 7 months ago for a
    6-month preset). Calendar arithmetic per the spec's "n-month window
    ending today" definition.
    """
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(d.day, _last_day(year, month)))


def _preset_href(body, label):
    """Extract the href of the preset button labelled `label` from rendered HTML.

    Jinja autoescapes '&' as '&amp;' inside attribute values, so the href is
    unescaped before returning so it can be passed straight to client.get().
    """
    match = re.search(
        r'href="([^"]*)"[^>]*>' + re.escape(label) + r"</a>", body
    )
    assert match, f"Preset button '{label}' not found in response"
    return html.unescape(match.group(1))


def _active_preset_labels(body):
    """Labels of all preset buttons rendered with the `is-active` class."""
    return re.findall(
        r'<a class="preset-btn is-active" href="[^"]*">([^<]+)</a>', body
    )


def _normalize_filter_state(body):
    """Strip filter-bar state (is-active class, pre-filled date inputs) so two
    responses can be compared on their data sections only."""
    body = re.sub(r'value="\d{4}-\d{2}-\d{2}"', 'value=""', body)
    return body.replace("preset-btn is-active", "preset-btn")


def _profile_url(app, **kwargs):
    """Build a /profile URL with query params via url_for (never hardcoded)."""
    with app.app_context():
        return url_for("profile", **kwargs)


# ------------------------------------------------------------------ #
# Fixtures (mirrors tests/test_backend_connection.py)                 #
# ------------------------------------------------------------------ #

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


@pytest.fixture
def insert_expense():
    """Insert an expense row directly (parameterised SQL only)."""
    def _insert(user_id, amount, category, expense_date, description=None):
        conn = db.get_db()
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, expense_date, description),
        )
        conn.commit()
        conn.close()
    return _insert


@pytest.fixture
def dated_expenses(empty_user_id, insert_expense):
    """Empty user with three expenses at controlled, non-overlapping dates."""
    insert_expense(empty_user_id, 100.00, "Food", "2000-02-15", "In-range food")
    insert_expense(empty_user_id, 50.00, "Transport", "2000-03-10", "In-range transport")
    insert_expense(empty_user_id, 25.00, "Bills", "2000-07-01", "Out-of-range bills")
    return empty_user_id


# ------------------------------------------------------------------ #
# Unit tests — get_summary_stats with date-range args                 #
# ------------------------------------------------------------------ #

def test_get_summary_stats_date_range_filters_expenses(dated_expenses):
    stats = queries.get_summary_stats(
        dated_expenses, date_from="2000-01-01", date_to="2000-03-31"
    )
    assert stats["total_spent"] == 150.00
    assert stats["transaction_count"] == 2
    assert stats["top_category"] == "Food"


def test_get_summary_stats_date_range_with_no_matches(dated_expenses):
    assert queries.get_summary_stats(
        dated_expenses, date_from="2000-01-01", date_to="2000-01-31"
    ) == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


def test_get_summary_stats_none_none_matches_unfiltered(seed_id):
    assert queries.get_summary_stats(seed_id, None, None) == (
        queries.get_summary_stats(seed_id)
    )


# ------------------------------------------------------------------ #
# Unit tests — get_recent_transactions with date-range args           #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_date_range_filters_expenses(dated_expenses):
    txns = queries.get_recent_transactions(
        dated_expenses, date_from="2000-01-01", date_to="2000-03-31"
    )
    assert len(txns) == 2
    assert [t["date"] for t in txns] == ["2000-03-10", "2000-02-15"]
    assert [t["amount"] for t in txns] == [50.00, 100.00]
    for txn in txns:
        assert set(txn.keys()) == {"date", "description", "category", "amount"}


def test_get_recent_transactions_limit_applies_with_date_range(dated_expenses):
    txns = queries.get_recent_transactions(
        dated_expenses, limit=1, date_from="2000-01-01", date_to="2000-03-31"
    )
    assert len(txns) == 1
    assert txns[0]["date"] == "2000-03-10"


def test_get_recent_transactions_date_range_with_no_matches(dated_expenses):
    assert queries.get_recent_transactions(
        dated_expenses, date_from="2000-01-01", date_to="2000-01-31"
    ) == []


def test_get_recent_transactions_none_none_matches_unfiltered(seed_id):
    assert queries.get_recent_transactions(seed_id, date_from=None, date_to=None) == (
        queries.get_recent_transactions(seed_id)
    )


# ------------------------------------------------------------------ #
# Unit tests — get_category_breakdown with date-range args            #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_date_range_filters_expenses(dated_expenses):
    cats = queries.get_category_breakdown(
        dated_expenses, date_from="2000-01-01", date_to="2000-03-31"
    )
    assert [c["name"] for c in cats] == ["Food", "Transport"]
    assert cats[0]["amount"] == 100.00
    assert cats[1]["amount"] == 50.00
    assert [c["pct"] for c in cats] == [67, 33]
    assert sum(c["pct"] for c in cats) == 100


def test_get_category_breakdown_date_range_with_no_matches(dated_expenses):
    assert queries.get_category_breakdown(
        dated_expenses, date_from="2000-01-01", date_to="2000-01-31"
    ) == []


def test_get_category_breakdown_none_none_matches_unfiltered(seed_id):
    assert queries.get_category_breakdown(seed_id, None, None) == (
        queries.get_category_breakdown(seed_id)
    )


# ------------------------------------------------------------------ #
# Route tests — /profile with no query params (Step 5 equivalence)    #
# ------------------------------------------------------------------ #

def test_profile_no_query_params_shows_unfiltered_step5_data(authed_client):
    resp = authed_client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Summary stats: unfiltered Step 5 values for the seed user
    assert "₨346.24" in body
    assert ">8<" in body
    assert "Bills" in body

    # Recent transactions: all 8 rows
    assert body.count('<td class="ta-right">') == 8
    # Category breakdown: all 7 seed categories
    assert body.count('class="category-row"') == 7
    for cat in ("Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"):
        assert f">{cat}<" in body
    # Every amount carries the rupee symbol: 1 stat + 8 txns + 7 categories
    assert body.count("₨") == 16

    # Filter bar renders all four presets plus the custom-range form
    for label in ("This Month", "Last 3 Months", "Last 6 Months", "All Time"):
        assert label in body
    assert 'type="date"' in body
    assert 'name="date_from"' in body
    assert 'name="date_to"' in body
    assert "Apply" in body

    # No filter active: empty date inputs, "All Time" highlighted
    assert body.count('value=""') == 2
    assert _active_preset_labels(body) == ["All Time"]


def test_profile_empty_query_params_equivalent_to_no_params(authed_client):
    plain = authed_client.get("/profile").get_data(as_text=True)
    empty = authed_client.get("/profile?date_from=&date_to=").get_data(as_text=True)
    assert plain == empty


# ------------------------------------------------------------------ #
# Route tests — preset filters                                        #
# ------------------------------------------------------------------ #

def test_this_month_preset_filters_all_three_sections(
    app, authed_empty_client, empty_user_id, insert_expense
):
    today = date.today()
    first_of_month = today.replace(day=1)

    insert_expense(empty_user_id, 100.00, "Food", today.isoformat(), "Current month")
    insert_expense(
        empty_user_id, 50.00, "Bills", _shift_months(today, -1).isoformat(), "Previous month"
    )

    page = authed_empty_client.get("/profile").get_data(as_text=True)
    href = _preset_href(page, "This Month")

    with app.app_context():
        expected = url_for(
            "profile", date_from=first_of_month.isoformat(), date_to=today.isoformat()
        )
    assert href == expected, "This Month link must be built via url_for with date_from/date_to"

    resp = authed_empty_client.get(href)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Summary stats reflect only the current-month expense
    assert "₨100.00" in body
    assert ">1<" in body
    # Recent transactions: only the current-month row
    assert body.count('<td class="ta-right">') == 1
    assert "Current month" in body
    assert "Previous month" not in body
    assert "₨50.00" not in body
    # Category breakdown: only Food
    assert body.count('class="category-row"') == 1
    assert ">Food<" in body
    assert ">Bills<" not in body
    # Visual indication: This Month is the active preset
    assert _active_preset_labels(body) == ["This Month"]


def test_this_month_matches_unfiltered_when_all_expenses_in_month(app, authed_client):
    """All seed expenses fall within the current calendar month, so the
    'This Month' preset must render exactly the unfiltered data."""
    today = date.today()
    with app.app_context():
        href = url_for(
            "profile", date_from=today.replace(day=1).isoformat(), date_to=today.isoformat()
        )

    plain = authed_client.get("/profile").get_data(as_text=True)
    filtered = authed_client.get(href).get_data(as_text=True)

    assert _normalize_filter_state(filtered) == _normalize_filter_state(plain)
    assert "₨346.24" in filtered
    assert _active_preset_labels(plain) == ["All Time"]
    assert _active_preset_labels(filtered) == ["This Month"]


def test_last_3_months_preset_filters_to_3_month_window(
    app, authed_empty_client, empty_user_id, insert_expense
):
    today = date.today()
    insert_expense(empty_user_id, 40.00, "Food", today.isoformat(), "Recent expense")
    insert_expense(
        empty_user_id, 60.00, "Health", _shift_months(today, -4).isoformat(), "Four months ago"
    )

    page = authed_empty_client.get("/profile").get_data(as_text=True)
    href = _preset_href(page, "Last 3 Months")

    resp = authed_empty_client.get(href)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Only the today expense falls inside the 3-month window ending today
    assert "₨40.00" in body
    assert ">1<" in body
    assert "Recent expense" in body
    assert "Four months ago" not in body
    assert "₨60.00" not in body
    assert body.count('<td class="ta-right">') == 1
    assert body.count('class="category-row"') == 1
    assert ">Food<" in body
    assert ">Health<" not in body
    assert _active_preset_labels(body) == ["Last 3 Months"]


def test_last_6_months_preset_filters_to_6_month_window(
    app, authed_empty_client, empty_user_id, insert_expense
):
    today = date.today()
    insert_expense(empty_user_id, 40.00, "Food", today.isoformat(), "Recent expense")
    insert_expense(
        empty_user_id, 60.00, "Health", _shift_months(today, -4).isoformat(), "Four months ago"
    )
    insert_expense(
        empty_user_id, 90.00, "Bills", _shift_months(today, -7).isoformat(), "Seven months ago"
    )

    page = authed_empty_client.get("/profile").get_data(as_text=True)
    href = _preset_href(page, "Last 6 Months")

    resp = authed_empty_client.get(href)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Today and 4-months-ago are inside the 6-month window; 7-months-ago is not
    assert "₨100.00" in body
    assert ">2<" in body
    assert "Recent expense" in body
    assert "Four months ago" in body
    assert "Seven months ago" not in body
    assert "₨90.00" not in body
    assert body.count('<td class="ta-right">') == 2
    assert body.count('class="category-row"') == 2
    assert ">Bills<" not in body
    assert _active_preset_labels(body) == ["Last 6 Months"]


def test_all_time_preset_uses_clean_url_and_shows_all_expenses(app, authed_client):
    plain = authed_client.get("/profile").get_data(as_text=True)
    href = _preset_href(plain, "All Time")
    assert href == "/profile", "All Time preset must link to a clean /profile URL"
    assert "?" not in href

    # After applying a filter, All Time is still available as a clean link
    today = date.today()
    with app.app_context():
        filtered_url = url_for(
            "profile", date_from=today.replace(day=1).isoformat(), date_to=today.isoformat()
        )
    filtered_page = authed_client.get(filtered_url).get_data(as_text=True)
    assert _preset_href(filtered_page, "All Time") == "/profile"

    # Clicking All Time restores the full unfiltered view
    resp = authed_client.get(href)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "₨346.24" in body
    assert ">8<" in body
    assert body.count('<td class="ta-right">') == 8
    assert body.count('class="category-row"') == 7
    assert _active_preset_labels(body) == ["All Time"]


# ------------------------------------------------------------------ #
# Route tests — custom date ranges                                    #
# ------------------------------------------------------------------ #

def test_custom_date_range_filters_all_three_sections(
    app, authed_empty_client, empty_user_id, insert_expense
):
    insert_expense(empty_user_id, 100.00, "Food", "2000-02-15", "In-range food")
    insert_expense(empty_user_id, 50.00, "Transport", "2000-03-10", "In-range transport")
    insert_expense(empty_user_id, 25.00, "Bills", "2000-07-01", "Out-of-range bills")

    url = _profile_url(app, date_from="2000-01-01", date_to="2000-03-31")
    resp = authed_empty_client.get(url)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Summary stats: only the two in-range expenses
    assert "₨150.00" in body
    assert ">2<" in body

    # Recent transactions: only in-range, newest first
    assert body.count('<td class="ta-right">') == 2
    assert "In-range food" in body
    assert "In-range transport" in body
    assert "Out-of-range bills" not in body
    assert "₨25.00" not in body
    assert body.index("In-range transport") < body.index("In-range food")

    # Category breakdown: only in-range categories
    assert body.count('class="category-row"') == 2
    assert ">Food<" in body
    assert ">Transport<" in body
    assert ">Bills<" not in body

    # Custom range is visually indicated: no preset active, inputs pre-filled
    assert _active_preset_labels(body) == []
    assert 'value="2000-01-01"' in body
    assert 'value="2000-03-31"' in body

    # All amounts show the rupee symbol: 1 stat + 2 txns + 2 categories
    assert body.count("₨") == 5


def test_date_from_after_date_to_flashes_error_and_falls_back(app, authed_client):
    url = _profile_url(app, date_from="2099-01-01", date_to="2000-01-01")
    resp = authed_client.get(url)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Flash error is rendered globally by base.html
    assert "Start date must be before end date." in body

    # Falls back to the unfiltered Step 5 view
    assert "₨346.24" in body
    assert ">8<" in body
    assert "Bills" in body
    assert body.count('<td class="ta-right">') == 8
    assert body.count('class="category-row"') == 7

    # The invalid range is not reflected in the filter UI
    assert 'value="2099-01-01"' not in body
    assert 'value="2000-01-01"' not in body
    assert body.count('value=""') == 2
    assert _active_preset_labels(body) == ["All Time"]


@pytest.mark.parametrize(
    "query",
    [
        "date_from=not-a-date",
        "date_to=not-a-date",
        "date_from=not-a-date&date_to=not-a-date",
        "date_from=2026-13-45&date_to=2026-01-01",
        "date_from=2026-02-30&date_to=2026-03-01",
        "date_from=2026-1-1",
        "date_from=2000-01-01'; DROP TABLE expenses;--",
    ],
)
def test_malformed_dates_fall_back_to_unfiltered_silently(app, authed_client, query):
    resp = authed_client.get("/profile?" + query)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Unfiltered Step 5 data is still shown (no crash, table not dropped)
    assert "₨346.24" in body
    assert ">8<" in body
    assert body.count('<td class="ta-right">') == 8
    assert body.count('class="category-row"') == 7

    # Silent fallback: no flash error, no invalid value echoed into the inputs
    assert "Start date must be before end date." not in body
    assert body.count('value=""') == 2
    assert _active_preset_labels(body) == ["All Time"]


@pytest.mark.parametrize(
    "query",
    [
        "date_from=2026-01-01",
        "date_to=2026-12-31",
        "date_from=2026-01-01&date_to=",
        "date_from=&date_to=2026-12-31",
    ],
)
def test_partial_date_params_fall_back_to_unfiltered(app, authed_client, query):
    resp = authed_client.get("/profile?" + query)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Both params are required for a filter; otherwise unfiltered data shows
    assert "₨346.24" in body
    assert ">8<" in body
    assert "Start date must be before end date." not in body
    assert body.count('value=""') == 2
    assert _active_preset_labels(body) == ["All Time"]


# ------------------------------------------------------------------ #
# Route tests — visual indication & symbol rendering                  #
# ------------------------------------------------------------------ #

def test_active_preset_button_visual_indication(app, authed_empty_client):
    # No filter → only "All Time" is highlighted
    body = authed_empty_client.get("/profile").get_data(as_text=True)
    assert _active_preset_labels(body) == ["All Time"]

    # A "This Month" range → only that preset is highlighted
    today = date.today()
    with app.app_context():
        url = url_for(
            "profile", date_from=today.replace(day=1).isoformat(), date_to=today.isoformat()
        )
    body = authed_empty_client.get(url).get_data(as_text=True)
    assert _active_preset_labels(body) == ["This Month"]

    # A custom range → no preset highlighted, date inputs pre-filled instead
    url = _profile_url(app, date_from="2000-01-01", date_to="2000-01-31")
    body = authed_empty_client.get(url).get_data(as_text=True)
    assert _active_preset_labels(body) == []
    assert 'value="2000-01-01"' in body
    assert 'value="2000-01-31"' in body


def test_all_amounts_show_rupee_symbol_regardless_of_filter(
    app, authed_client, seed_id, insert_expense
):
    today = date.today()

    # Unfiltered: 1 stat + 8 transactions + 7 categories = 16 rupee symbols
    body = authed_client.get("/profile").get_data(as_text=True)
    assert body.count("₨") == 16
    assert "₨346.24" in body

    # This Month preset (all seed expenses are in the current month)
    with app.app_context():
        month_url = url_for(
            "profile", date_from=today.replace(day=1).isoformat(), date_to=today.isoformat()
        )
    body = authed_client.get(month_url).get_data(as_text=True)
    assert body.count("₨") == 16
    assert "₨346.24" in body

    # Custom range containing a fresh expense
    insert_expense(seed_id, 12.50, "Other", today.isoformat(), "Rupee check")
    url = _profile_url(app, date_from=today.replace(day=1).isoformat(), date_to=today.isoformat())
    body = authed_client.get(url).get_data(as_text=True)
    assert "₨" in body
    assert "₨12.50" in body

    # Empty range: the only amount is the ₨0.00 total
    empty_url = _profile_url(app, date_from="2000-01-01", date_to="2000-01-31")
    body = authed_client.get(empty_url).get_data(as_text=True)
    assert body.count("₨") == 1
    assert "₨0.00" in body


# ------------------------------------------------------------------ #
# Route tests — empty ranges and auth guard                           #
# ------------------------------------------------------------------ #

def test_empty_date_range_shows_zero_totals_no_errors(app, authed_client):
    url = _profile_url(app, date_from="2000-01-01", date_to="2000-01-31")
    resp = authed_client.get(url)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Summary stats: zero total, zero transactions, em-dash top category
    assert "₨0.00" in body
    assert ">0<" in body
    assert ">—<" in body

    # No transactions and no category rows render
    assert body.count('<td class="ta-right">') == 0
    assert body.count('class="category-row"') == 0
    for cat in ("Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"):
        assert f">{cat}<" not in body

    # Page still renders the filter bar and no error flash
    assert "This Month" in body
    assert "Start date must be before end date." not in body


@pytest.mark.parametrize(
    "query",
    [
        "?date_from=2000-01-01&date_to=2000-01-31",
        "?date_from=not-a-date",
        "?date_to=2026-01-01",
        "?date_from=2026-01-01&date_to=2025-01-01",
    ],
)
def test_profile_redirects_to_login_with_query_params(client, query):
    resp = client.get("/profile" + query)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
