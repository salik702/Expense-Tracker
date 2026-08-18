"""Tests for the Step 7 "Add Expense" feature.

Spec source of truth: .opencode/specs/07-add-expense.md

Covers:
- GET /expenses/add renders the form for a logged-in user: amount input
  (type=number, min 0.01, step 0.01, ₨ prefix), a category select populated
  from CATEGORIES (all 7, no placeholder option), a date input, an optional
  description input, and an "Add expense" submit button
- POST /expenses/add happy path: parameterised insert bound to the session
  user, 302 redirect to /profile, success flash, and the profile page
  immediately reflects the new expense (transaction list, total spent,
  transaction count)
- Auth guards: unauthenticated GET and POST redirect to /login
- Server-side validation: empty/non-numeric/zero/negative amounts, dates not
  matching YYYY-MM-DD, and categories outside the CATEGORIES allowlist all
  re-render with a user-facing error and insert nothing
- Form pre-fills all submitted values on validation failure
- Blank description stored as NULL
- user_id is always taken from the session, never from the form
- SQL-injection-shaped payloads are rejected or stored literally (never
  interpolated into SQL)
- The "Add expense" nav link appears for logged-in users (with the .is-active
  class on the add page) and a "+ Add expense" button appears on the profile
  page
- New expenses persist across page refreshes and appear in the database

Fixture conventions follow tests/test_backend_connection.py.
"""

import re
from datetime import date

import pytest

import database.db as db
from app import app as flask_app

# Baseline derived from the 8 seeded demo expenses (see seed_db()).
SEED_TOTAL = 346.24
SEED_COUNT = 8


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _expense_count(user_id):
    """Number of expense rows owned by `user_id` (parameterised SQL only)."""
    conn = db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    conn.close()
    return count


def _last_expense(user_id):
    """The most recently inserted expense row owned by `user_id`."""
    conn = db.get_db()
    row = conn.execute(
        "SELECT user_id, amount, category, date, description FROM expenses "
        "WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row


def _valid_expense_data(**overrides):
    """Form data for a valid expense submission, per the spec's happy path."""
    data = {
        "csrf_token": "test-csrf-token",
        "amount": "12.50",
        "category": "Food",
        "date": date.today().isoformat(),
        "description": "Lunch",
    }
    data.update(overrides)
    return data


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
def authed_client(client, seed_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_id
        sess["csrf_token"] = "test-csrf-token"
    return client


# ------------------------------------------------------------------ #
# GET /expenses/add — form rendering (DoD: form shows amount field,   #
# category dropdown listing all 7 categories, date + description)     #
# ------------------------------------------------------------------ #

def test_add_expense_form_renders_for_logged_in_user(authed_client):
    resp = authed_client.get("/expenses/add")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    # Amount field: number input with a ₨ prefix and min/step per spec
    assert "Add expense" in body
    assert 'name="amount"' in body
    assert 'type="number"' in body
    assert 'min="0.01"' in body
    assert 'step="0.01"' in body
    assert "₨" in body, "Amount input must show the ₨ currency prefix"

    # Category select, date input, optional description input
    assert 'name="category"' in body
    assert 'name="date"' in body
    assert 'type="date"' in body
    assert 'name="description"' in body

    # Form submits via POST to the add-expense endpoint
    assert 'method="POST"' in body
    assert 'action="/expenses/add"' in body
    assert ">Add expense<" in body, "Submit button must read 'Add expense'"


def test_add_expense_form_lists_all_seven_categories(authed_client):
    resp = authed_client.get("/expenses/add")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    options = re.findall(r'<option value="([^"]+)"', body)
    assert options == db.CATEGORIES, (
        "Category dropdown must be populated from the CATEGORIES list passed "
        "in by the route, in order, with no extra placeholder option"
    )

    # First option (Food) is the browser-default selection on a clean GET —
    # no option carries an explicit selected attribute
    assert '<option value="Food">Food</option>' in body
    assert "selected" not in body


def test_add_expense_nav_link_active_on_add_page(authed_client):
    """The navbar's Add expense link uses the .is-active pattern on this page."""
    body = authed_client.get("/expenses/add").get_data(as_text=True)
    assert 'href="/expenses/add" class="nav-link is-active"' in body


# ------------------------------------------------------------------ #
# Auth guards (DoD: logged-out /expenses/add redirects to /login)     #
# ------------------------------------------------------------------ #

def test_add_expense_get_redirects_to_login_when_logged_out(client):
    resp = client.get("/expenses/add")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_add_expense_post_redirects_to_login_when_logged_out(client, seed_id):
    resp = client.post(
        "/expenses/add",
        data=_valid_expense_data(),
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert _expense_count(seed_id) == SEED_COUNT, (
        "Logged-out POST must not insert an expense"
    )


# ------------------------------------------------------------------ #
# POST /expenses/add — happy path                                     #
# ------------------------------------------------------------------ #

def test_add_expense_valid_submission_redirects_to_profile(authed_client):
    resp = authed_client.post("/expenses/add", data=_valid_expense_data())
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_add_expense_valid_submission_flashes_success(authed_client):
    resp = authed_client.post(
        "/expenses/add", data=_valid_expense_data(), follow_redirects=True
    )
    assert resp.status_code == 200
    assert "Expense added." in resp.get_data(as_text=True)


def test_add_expense_valid_submission_inserts_row_with_correct_values(
    authed_client, seed_id
):
    today = date.today().isoformat()
    resp = authed_client.post(
        "/expenses/add", data=_valid_expense_data(date=today)
    )
    assert resp.status_code == 302

    row = _last_expense(seed_id)
    assert row is not None, "A new expense row must exist after a valid POST"
    assert row["user_id"] == seed_id
    assert row["amount"] == 12.50
    assert row["category"] == "Food"
    assert row["date"] == today
    assert row["description"] == "Lunch"
    assert _expense_count(seed_id) == SEED_COUNT + 1


def test_add_expense_appears_on_profile_as_newest_row(authed_client):
    """DoD: transaction list shows the new expense as the newest row with the
    correct ₨ amount and category."""
    authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(description="Lunch"),
    )
    body = authed_client.get("/profile").get_data(as_text=True)

    assert "₨12.50" in body, "New expense amount must render with the ₨ symbol"
    assert ">Lunch<" in body, "New expense description must render in the list"
    assert ">Food<" in body, "New expense category must render as a badge"
    # Newest first: our today-dated expense precedes the newest seed row
    assert body.index(">Lunch<") < body.index(">Groceries for the week<"), (
        "New expense must appear as the newest row in the transaction list"
    )


def test_add_expense_updates_summary_stats(authed_client):
    """DoD: total spent increases by exactly the amount; count increments by 1."""
    authed_client.post("/expenses/add", data=_valid_expense_data())
    body = authed_client.get("/profile").get_data(as_text=True)

    assert f"₨{SEED_TOTAL + 12.50:,.2f}" in body, (
        "Total spent must increase by exactly the entered amount"
    )
    assert f">{SEED_COUNT + 1}<" in body, (
        "Transaction count must increment by 1"
    )


def test_add_expense_multiple_submissions_accumulate(authed_client, seed_id):
    today = date.today().isoformat()
    authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="10.00", category="Transport",
                                 date=today, description="Auto-rickshaw"),
    )
    authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="5.25", category="Food",
                                 date=today, description="Chai"),
    )
    body = authed_client.get("/profile").get_data(as_text=True)

    assert f"₨{SEED_TOTAL + 10.00 + 5.25:,.2f}" in body
    assert f">{SEED_COUNT + 2}<" in body
    assert "Auto-rickshaw" in body
    assert ">Chai<" in body
    assert _expense_count(seed_id) == SEED_COUNT + 2


def test_add_expense_blank_description_stored_as_null(authed_client, seed_id):
    """DoD: blank description is stored as NULL and the expense still shows."""
    authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="7.00", category="Other",
                                 description=""),
    )
    row = _last_expense(seed_id)
    assert row is not None
    assert row["description"] is None, "Blank description must be stored as NULL"
    assert _expense_count(seed_id) == SEED_COUNT + 1

    body = authed_client.get("/profile").get_data(as_text=True)
    assert "₨7.00" in body, "Expense with NULL description must still appear"


# ------------------------------------------------------------------ #
# POST /expenses/add — validation errors (DoD: error + no insert)     #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize(
    "amount",
    [
        "",           # missing / empty
        "   ",        # whitespace only
        "abc",        # non-numeric
        "12abc",      # partially numeric
        "1,234.50",   # not parseable as a Python float
        "0",          # zero
        "0.00",       # zero (decimal form)
        "-5",         # negative
        "-0.01",      # negative (decimal form)
        "nan",        # not a finite number
        "inf",        # not a finite number
        "NaN",        # not a finite number (case-insensitive)
        "1e309",      # overflows to infinity
    ],
)
def test_add_expense_invalid_amount_shows_error_and_no_insert(
    authed_client, seed_id, amount
):
    resp = authed_client.post(
        "/expenses/add", data=_valid_expense_data(amount=amount)
    )
    assert resp.status_code == 200, "Invalid amount must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please enter a valid amount greater than 0." in body
    assert _expense_count(seed_id) == SEED_COUNT, (
        "Invalid amount must not insert a row"
    )


@pytest.mark.parametrize(
    "date_str",
    [
        "",                # missing / empty
        "not-a-date",      # free text
        "2026-13-45",      # month out of range
        "2026-02-30",      # day out of range for February
        "2026-1-1",        # not zero-padded (fails YYYY-MM-DD)
        "01-01-2026",      # wrong format
    ],
)
def test_add_expense_invalid_date_shows_error_and_no_insert(
    authed_client, seed_id, date_str
):
    resp = authed_client.post(
        "/expenses/add", data=_valid_expense_data(date=date_str)
    )
    assert resp.status_code == 200, "Invalid date must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please enter a valid date." in body
    assert _expense_count(seed_id) == SEED_COUNT, (
        "Invalid date must not insert a row"
    )


@pytest.mark.parametrize(
    "category",
    [
        "",                                # missing / empty
        "Cryptocurrency",                  # not in CATEGORIES at all
        "FOOD",                            # allowlist is case-sensitive
        "Food'; DROP TABLE expenses;--",   # SQL-injection-shaped value
    ],
)
def test_add_expense_invalid_category_shows_error_and_no_insert(
    authed_client, seed_id, category
):
    resp = authed_client.post(
        "/expenses/add", data=_valid_expense_data(category=category)
    )
    assert resp.status_code == 200, "Invalid category must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please choose a valid category." in body
    assert _expense_count(seed_id) == SEED_COUNT, (
        "Invalid category must not insert a row"
    )


@pytest.mark.parametrize(
    "overrides, error, food_selected",
    [
        (
            {"amount": "abc"},
            "Please enter a valid amount greater than 0.",
            True,
        ),
        (
            {"date": "not-a-date"},
            "Please enter a valid date.",
            True,
        ),
        (
            {"category": "Cryptocurrency"},
            "Please choose a valid category.",
            False,
        ),
    ],
)
def test_add_expense_validation_failure_preserves_submitted_values(
    authed_client, seed_id, overrides, error, food_selected
):
    """DoD: on validation failure the previously entered values stay filled in."""
    data = {
        "csrf_token": "test-csrf-token",
        "amount": "99.99",
        "category": "Food",
        "date": "2026-01-01",
        "description": "Groceries",
    }
    data.update(overrides)
    resp = authed_client.post("/expenses/add", data=data)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert error in body
    assert f'value="{data["amount"]}"' in body, "Amount must be pre-filled"
    assert f'value="{data["date"]}"' in body, "Date must be pre-filled"
    assert f'value="{data["description"]}"' in body, (
        "Description must be pre-filled"
    )
    if food_selected:
        assert '<option value="Food" selected>Food</option>' in body, (
            "Previously chosen category must stay selected"
        )
    else:
        assert '<option value="Food">Food</option>' in body
        assert "selected" not in body, (
            "An invalid category must not be echoed back into the select"
        )
    assert _expense_count(seed_id) == SEED_COUNT


# ------------------------------------------------------------------ #
# POST /expenses/add — security boundaries                            #
# ------------------------------------------------------------------ #

def test_add_expense_csrf_token_required(authed_client, seed_id):
    """POSTs without a matching csrf_token are rejected before any insert."""
    data = _valid_expense_data()
    data.pop("csrf_token")
    resp = authed_client.post("/expenses/add", data=data)
    assert resp.status_code == 400
    assert _expense_count(seed_id) == SEED_COUNT


def test_add_expense_wrong_csrf_token_rejected(authed_client, seed_id):
    data = _valid_expense_data(csrf_token="wrong-token")
    resp = authed_client.post("/expenses/add", data=data)
    assert resp.status_code == 400
    assert _expense_count(seed_id) == SEED_COUNT


def test_add_expense_csrf_token_present_in_form(authed_client):
    body = authed_client.get("/expenses/add").get_data(as_text=True)
    assert 'name="csrf_token"' in body, (
        "The form must carry a hidden csrf_token field"
    )


def test_add_expense_description_too_long_rejected(authed_client, seed_id):
    resp = authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(description="x" * 201),
    )
    assert resp.status_code == 200
    assert "Description must be 200 characters or fewer." in resp.get_data(as_text=True)
    assert _expense_count(seed_id) == SEED_COUNT


def test_add_expense_sql_injection_description_stored_literally(
    authed_client, seed_id
):
    """Parameterised insert: injection-shaped descriptions are stored as-is."""
    payload = "'; DROP TABLE expenses;--"
    resp = authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="9.99", description=payload),
    )
    assert resp.status_code == 302

    row = _last_expense(seed_id)
    assert row["description"] == payload, (
        "Description must be stored literally via a parameterised query"
    )
    assert _expense_count(seed_id) == SEED_COUNT + 1

    # Table still exists and the profile page still renders live data
    body = authed_client.get("/profile").get_data(as_text=True)
    assert f"₨{SEED_TOTAL + 9.99:,.2f}" in body
    assert "₨9.99" in body


def test_add_expense_sql_injection_amount_rejected(authed_client, seed_id):
    resp = authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="100; DROP TABLE expenses;--"),
    )
    assert resp.status_code == 200
    assert "Please enter a valid amount greater than 0." in resp.get_data(as_text=True)
    assert _expense_count(seed_id) == SEED_COUNT, (
        "Injection-shaped amount must be rejected before any insert"
    )


def test_add_expense_user_id_always_from_session_not_form(authed_client, seed_id):
    """Rules: insert binds user_id from session['user_id'] — never from the form."""
    conn = db.get_db()
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES "
        "('Intruder', 'intruder@spendly.com', 'x')"
    )
    conn.commit()
    intruder_id = cur.lastrowid
    conn.close()

    resp = authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(
            amount="25.00", category="Bills", description="Spoofed ownership",
            user_id=str(intruder_id),
        ),
    )
    assert resp.status_code == 302

    row = _last_expense(seed_id)
    assert row["description"] == "Spoofed ownership"
    assert row["user_id"] == seed_id, (
        "A forged user_id form field must be ignored; the expense must be "
        "bound to the session user"
    )
    assert _expense_count(intruder_id) == 0


# ------------------------------------------------------------------ #
# Persistence (DoD: expense persists after refresh + in the database) #
# ------------------------------------------------------------------ #

def test_add_expense_persists_after_refresh(authed_client, seed_id):
    authed_client.post(
        "/expenses/add",
        data=_valid_expense_data(amount="42.00", category="Shopping",
                                 description="Persistent expense"),
    )
    assert _expense_count(seed_id) == SEED_COUNT + 1

    for _ in range(2):  # two consecutive page loads == two refreshes
        body = authed_client.get("/profile").get_data(as_text=True)
        assert "₨42.00" in body
        assert f"₨{SEED_TOTAL + 42.00:,.2f}" in body
        assert "Persistent expense" in body


# ------------------------------------------------------------------ #
# Navigation links (DoD: Add expense link in navbar + on profile)     #
# ------------------------------------------------------------------ #

def test_add_expense_link_in_navbar_for_logged_in_users(authed_client):
    body = authed_client.get("/profile").get_data(as_text=True)
    assert 'href="/expenses/add" class="nav-link' in body, (
        "Logged-in users must see the Add expense link in the navbar"
    )


def test_add_expense_link_on_profile_page(authed_client):
    body = authed_client.get("/profile").get_data(as_text=True)
    assert 'class="profile-add-btn"' in body
    assert "+ Add expense" in body


def test_add_expense_link_not_visible_when_logged_out(client):
    body = client.get("/").get_data(as_text=True)
    assert 'href="/expenses/add"' not in body
    assert "Add expense" not in body, (
        "Logged-out visitors must not see the Add expense link"
    )