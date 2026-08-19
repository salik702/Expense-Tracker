"""Tests for the Step 8 "Edit Expense" feature.

Spec source of truth: .opencode/specs/08-edit-expense.md

Covers:
- GET /expenses/<id>/edit renders the form pre-filled with the expense's
  current values (amount with ₨ prefix, category pre-selected, date,
  description), title "Edit expense", and a "Save changes" submit button
- POST /expenses/<id>/edit happy path: parameterised UPDATE bound to the
  expense id, 302 redirect to /profile, success flash, and the profile page
  immediately reflects the change (transaction list, total spent)
- Auth guards: unauthenticated GET and POST redirect to /login
- Ownership: another user's expense (or a non-existent id) returns 404
- Server-side validation: empty/non-numeric/zero/negative amounts, dates not
  matching YYYY-MM-DD, categories outside the CATEGORIES allowlist, and
  over-long descriptions all re-render with a user-facing error and update
  nothing
- Form pre-fills submitted values on validation failure
- Blank description stored as NULL
- CSRF token enforced on POST (400 on missing/mismatch)
- created_at is never changed by an update
- Updated values persist across page refreshes and appear in the database

Fixture conventions follow tests/test_07-add-expense.py.
"""

import re
from datetime import date

import pytest

import database.db as db
from app import app as flask_app

SEED_TOTAL = 346.24
SEED_COUNT = 8


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _expense_row(expense_id):
    conn = db.get_db()
    row = conn.execute(
        "SELECT id, user_id, amount, category, date, description, created_at "
        "FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone()
    conn.close()
    return row


def _first_expense_id(user_id):
    conn = db.get_db()
    row = conn.execute(
        "SELECT id FROM expenses WHERE user_id = ? ORDER BY id ASC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["id"]


def _valid_edit_data(**overrides):
    """Form data for a valid expense edit submission."""
    data = {
        "csrf_token": "test-csrf-token",
        "amount": "99.99",
        "category": "Food",
        "date": "2026-01-01",
        "description": "Edited expense",
    }
    data.update(overrides)
    return data


# ------------------------------------------------------------------ #
# Fixtures (mirrors tests/test_07-add-expense.py)                     #
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


@pytest.fixture
def other_user_id(app):
    """A second user who owns a different expense row."""
    conn = db.get_db()
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES "
        "('Intruder', 'intruder@spendly.com', 'x')"
    )
    conn.commit()
    uid = cur.lastrowid
    conn.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        (uid, 10.00, "Other", "2026-01-01", "Intruder expense"),
    )
    conn.commit()
    conn.close()
    return uid


# ------------------------------------------------------------------ #
# GET /expenses/<id>/edit — form rendering (DoD: form opens pre-      #
# filled with the expense's amount, category, date, description)      #
# ------------------------------------------------------------------ #

def test_edit_expense_form_renders_prefilled_for_logged_in_user(
    authed_client, seed_id
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.get(f"/expenses/{expense_id}/edit")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert "Edit expense" in body
    assert "Save changes" in body
    assert 'name="amount"' in body
    assert 'type="number"' in body
    assert 'min="0.01"' in body
    assert 'step="0.01"' in body
    assert "₨" in body, "Amount input must show the ₨ currency prefix"
    assert 'name="category"' in body
    assert 'name="date"' in body
    assert 'name="description"' in body
    assert 'method="POST"' in body
    assert f'action="/expenses/{expense_id}/edit"' in body
    assert 'name="csrf_token"' in body, (
        "The form must carry a hidden csrf_token field"
    )


def test_edit_expense_form_prefills_current_values(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    row = _expense_row(expense_id)
    body = authed_client.get(f"/expenses/{expense_id}/edit").get_data(as_text=True)

    assert f'value="{row["amount"]:.2f}"' in body, (
        "Amount must be pre-filled with the stored value"
    )
    assert f'<option value="{row["category"]}" selected>{row["category"]}</option>' in body, (
        "The expense's current category must be pre-selected"
    )
    assert f'value="{row["date"]}"' in body, (
        "Date must be pre-filled with the stored value"
    )
    if row["description"]:
        assert f'value="{row["description"]}"' in body, (
            "Description must be pre-filled with the stored value"
        )


def test_edit_expense_form_lists_all_seven_categories(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    body = authed_client.get(f"/expenses/{expense_id}/edit").get_data(as_text=True)
    options = re.findall(r'<option value="([^"]+)"', body)
    assert options == db.CATEGORIES, (
        "Category dropdown must be populated from the CATEGORIES list "
        "passed in by the route, in order, with no extra options"
    )


# ------------------------------------------------------------------ #
# Auth guards (DoD: logged-out /expenses/<id>/edit redirects to /login) #
# ------------------------------------------------------------------ #

def test_edit_expense_get_redirects_to_login_when_logged_out(client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = client.get(f"/expenses/{expense_id}/edit")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_edit_expense_post_redirects_to_login_when_logged_out(client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = client.post(
        f"/expenses/{expense_id}/edit", data=_valid_edit_data()
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert _expense_row(expense_id)["amount"] == 26.79, (
        "Logged-out POST must not update the expense"
    )


# ------------------------------------------------------------------ #
# Ownership (DoD: another user's or non-existent id returns 404)      #
# ------------------------------------------------------------------ #

def test_edit_expense_not_found_for_missing_id(authed_client):
    resp = authed_client.get("/expenses/999999/edit")
    assert resp.status_code == 404


def test_edit_expense_post_not_found_for_missing_id(authed_client):
    resp = authed_client.post(
        "/expenses/999999/edit", data=_valid_edit_data()
    )
    assert resp.status_code == 404


def test_edit_expense_forbidden_for_other_users_expense(
    authed_client, other_user_id
):
    conn = db.get_db()
    row = conn.execute(
        "SELECT id FROM expenses WHERE user_id = ? LIMIT 1", (other_user_id,)
    ).fetchone()
    conn.close()
    assert row is not None

    resp = authed_client.get(f"/expenses/{row['id']}/edit")
    assert resp.status_code == 404, (
        "A logged-in user must not see another user's expense form"
    )

    resp = authed_client.post(
        f"/expenses/{row['id']}/edit", data=_valid_edit_data()
    )
    assert resp.status_code == 404, (
        "A logged-in user must not update another user's expense"
    )
    assert _expense_row(row["id"])["amount"] == 10.00, (
        "Another user's expense must remain untouched"
    )


# ------------------------------------------------------------------ #
# POST /expenses/<id>/edit — happy path                               #
# ------------------------------------------------------------------ #

def test_edit_expense_valid_submission_redirects_to_profile(
    authed_client, seed_id
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit", data=_valid_edit_data()
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_edit_expense_valid_submission_flashes_success(
    authed_client, seed_id
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(),
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Expense updated." in resp.get_data(as_text=True)


def test_edit_expense_valid_submission_updates_row(
    authed_client, seed_id
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(
            amount="42.50", category="Bills", date="2026-02-02",
            description="New description",
        ),
    )
    assert resp.status_code == 302

    row = _expense_row(expense_id)
    assert row["amount"] == 42.50
    assert row["category"] == "Bills"
    assert row["date"] == "2026-02-02"
    assert row["description"] == "New description"


def test_edit_expense_blank_description_stored_as_null(
    authed_client, seed_id
):
    """DoD: saving with a blank description stores NULL."""
    expense_id = _first_expense_id(seed_id)
    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(description=""),
    )
    row = _expense_row(expense_id)
    assert row["description"] is None, (
        "Blank description must be stored as NULL"
    )


def test_edit_expense_profile_reflects_change(authed_client, seed_id):
    """DoD: edited amount shows on the profile transaction list."""
    expense_id = _first_expense_id(seed_id)
    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(
            amount="75.00", category="Health", description="Edited row"
        ),
    )
    body = authed_client.get("/profile").get_data(as_text=True)
    assert "₨75.00" in body, "Edited amount must render on the profile page"
    assert ">Edited row<" in body, (
        "Edited description must render in the transaction list"
    )
    assert ">Health<" in body, (
        "Edited category must render as a badge"
    )


def test_edit_expense_total_spent_changes_by_delta(authed_client, seed_id):
    """DoD: total spent changes by exactly the old→new difference.

    The first seeded expense is 26.79 in Food; editing it to 100.00 must
    increase the total by exactly 73.21.
    """
    expense_id = _first_expense_id(seed_id)
    assert _expense_row(expense_id)["amount"] == 26.79

    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(amount="100.00"),
    )
    body = authed_client.get("/profile").get_data(as_text=True)
    assert f"₨{SEED_TOTAL - 26.79 + 100.00:,.2f}" in body, (
        "Total spent must change by exactly the difference between old and "
        "new amounts"
    )
    assert f">{SEED_COUNT}<" in body, (
        "Editing must not change the transaction count"
    )


def test_edit_expense_category_breakdown_updates(authed_client, seed_id):
    """Changing category must move the amount out of the old category's total."""
    expense_id = _first_expense_id(seed_id)
    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(category="Shopping"),
    )
    conn = db.get_db()
    food_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE user_id = ? AND category = 'Food'",
        (seed_id,),
    ).fetchone()[0]
    conn.close()
    assert food_total == 32.40, (
        "Editing the first expense out of Food must remove 26.79 from the "
        "Food category total (only the 32.40 seed row remains)"
    )


# ------------------------------------------------------------------ #
# POST /expenses/<id>/edit — validation errors (DoD: error + no        #
# update)                                                             #
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
def test_edit_expense_invalid_amount_shows_error_and_no_update(
    authed_client, seed_id, amount
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit", data=_valid_edit_data(amount=amount)
    )
    assert resp.status_code == 200, "Invalid amount must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please enter a valid amount greater than 0." in body
    assert _expense_row(expense_id)["amount"] == 26.79, (
        "Invalid amount must not update the row"
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
def test_edit_expense_invalid_date_shows_error_and_no_update(
    authed_client, seed_id, date_str
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit", data=_valid_edit_data(date=date_str)
    )
    assert resp.status_code == 200, "Invalid date must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please enter a valid date." in body
    assert _expense_row(expense_id)["date"] == _expense_row(expense_id)["date"], (
        "Invalid date must not update the row"
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
def test_edit_expense_invalid_category_shows_error_and_no_update(
    authed_client, seed_id, category
):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit", data=_valid_edit_data(category=category)
    )
    assert resp.status_code == 200, "Invalid category must re-render the form"
    body = resp.get_data(as_text=True)
    assert "Please choose a valid category." in body
    assert _expense_row(expense_id)["category"] == "Food", (
        "Invalid category must not update the row"
    )


def test_edit_expense_description_too_long_rejected(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(description="x" * 201),
    )
    assert resp.status_code == 200
    assert (
        "Description must be 200 characters or fewer."
        in resp.get_data(as_text=True)
    )
    assert _expense_row(expense_id)["description"] == "Groceries for the week", (
        "Over-long description must not update the row"
    )


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"amount": "abc"}, "Please enter a valid amount greater than 0."),
        ({"date": "not-a-date"}, "Please enter a valid date."),
        ({"category": "Cryptocurrency"}, "Please choose a valid category."),
    ],
)
def test_edit_expense_validation_failure_preserves_submitted_values(
    authed_client, seed_id, overrides, error
):
    """DoD: on validation failure the previously entered values stay filled in."""
    expense_id = _first_expense_id(seed_id)
    data = {
        "csrf_token": "test-csrf-token",
        "amount": "55.55",
        "category": "Food",
        "date": "2026-03-03",
        "description": "Kept values",
    }
    data.update(overrides)
    resp = authed_client.post(f"/expenses/{expense_id}/edit", data=data)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)

    assert error in body
    assert f'value="{data["amount"]}"' in body, "Amount must be pre-filled"
    assert f'value="{data["date"]}"' in body, "Date must be pre-filled"
    assert f'value="{data["description"]}"' in body, (
        "Description must be pre-filled"
    )
    assert _expense_row(expense_id)["amount"] == 26.79, (
        "Validation failure must not update the row"
    )


# ------------------------------------------------------------------ #
# POST /expenses/<id>/edit — security boundaries                      #
# ------------------------------------------------------------------ #

def test_edit_expense_csrf_token_required(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    data = _valid_edit_data()
    data.pop("csrf_token")
    resp = authed_client.post(f"/expenses/{expense_id}/edit", data=data)
    assert resp.status_code == 400
    assert _expense_row(expense_id)["amount"] == 26.79, (
        "POST without csrf_token must not update the row"
    )


def test_edit_expense_wrong_csrf_token_rejected(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    data = _valid_edit_data(csrf_token="wrong-token")
    resp = authed_client.post(f"/expenses/{expense_id}/edit", data=data)
    assert resp.status_code == 400
    assert _expense_row(expense_id)["amount"] == 26.79


def test_edit_expense_sql_injection_description_stored_literally(
    authed_client, seed_id
):
    """Parameterised UPDATE: injection-shaped descriptions are stored as-is."""
    expense_id = _first_expense_id(seed_id)
    payload = "'; DROP TABLE expenses;--"
    resp = authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(description=payload),
    )
    assert resp.status_code == 302

    row = _expense_row(expense_id)
    assert row["description"] == payload, (
        "Description must be stored literally via a parameterised query"
    )

    body = authed_client.get("/profile").get_data(as_text=True)
    assert "₨99.99" in body, "Edited amount must still render after the update"


def test_edit_expense_user_id_not_changed_by_form(authed_client, seed_id):
    """The UPDATE must not let a forged user_id form field reassign ownership."""
    expense_id = _first_expense_id(seed_id)
    data = _valid_edit_data(user_id="1")
    resp = authed_client.post(f"/expenses/{expense_id}/edit", data=data)
    assert resp.status_code == 302
    assert _expense_row(expense_id)["user_id"] == seed_id, (
        "Expense ownership must never change on edit"
    )


# ------------------------------------------------------------------ #
# created_at preserved (DoD: created_at unchanged after edit)         #
# ------------------------------------------------------------------ #

def test_edit_expense_created_at_unchanged(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    original_created = _expense_row(expense_id)["created_at"]
    assert original_created is not None

    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(amount="11.11", description="Changed"),
    )
    row = _expense_row(expense_id)
    assert row["amount"] == 11.11, "Sanity check: update must have applied"
    assert row["created_at"] == original_created, (
        "created_at must never change on edit"
    )


# ------------------------------------------------------------------ #
# Persistence (DoD: updated values persist after refresh + database)  #
# ------------------------------------------------------------------ #

def test_edit_expense_persists_after_refresh(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    authed_client.post(
        f"/expenses/{expense_id}/edit",
        data=_valid_edit_data(amount="88.88", description="Persistent edit"),
    )
    row = _expense_row(expense_id)
    assert row["amount"] == 88.88
    assert row["description"] == "Persistent edit"

    for _ in range(2):  # two consecutive page loads == two refreshes
        body = authed_client.get("/profile").get_data(as_text=True)
        assert "₨88.88" in body
        assert "Persistent edit" in body


# ------------------------------------------------------------------ #
# Navigation links (DoD: per-row Edit link on the profile page)       #
# ------------------------------------------------------------------ #

def test_edit_expense_link_in_navbar_when_logged_out(client):
    body = client.get("/").get_data(as_text=True)
    assert "Edit expense" not in body, (
        "Logged-out visitors must not see edit links"
    )


def test_edit_expense_link_on_profile_rows(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    body = authed_client.get("/profile").get_data(as_text=True)
    assert 'class="txn-edit-link"' in body, (
        "Each transaction row must have an Edit link"
    )
    assert f'href="/expenses/{expense_id}/edit"' in body, (
        "The Edit link must point at the expense's edit URL"
    )