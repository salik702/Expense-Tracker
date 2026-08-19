"""Tests for the Step 9 "Delete Expense" feature.

Spec source of truth: .opencode/specs/09-delete-expense.md

Covers:
- Profile page shows a "Delete" control next to each "Edit" link in the
  recent-transactions table
- POST /expenses/<id>/delete happy path: 302 redirect to /profile, success
  flash, and the row is gone from the database
- Summary stats update: total spent drops by exactly the deleted amount and
  the transaction count drops by 1
- Category breakdown / top-category stat reflect the removal
- Deleted expense persists as absent across page refreshes
- Auth guards: unauthenticated POST redirects to /login and deletes nothing
- Ownership: another user's expense (or a non-existent id) returns 404 and
  deletes nothing
- GET requests to the delete URL delete nothing (405) and the row survives
- CSRF token enforced on POST (400 on missing/mismatch)
- Other transactions and the user account are unaffected

Fixture conventions follow tests/test_08-edit-expense.py.
"""

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
        "SELECT id, user_id, amount, category, date, description "
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


# ------------------------------------------------------------------ #
# Fixtures (mirrors tests/test_08-edit-expense.py)                   #
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
# Profile page delete controls (DoD: Delete control beside Edit)     #
# ------------------------------------------------------------------ #


def test_delete_control_shown_on_profile_rows(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    body = authed_client.get("/profile").get_data(as_text=True)
    assert 'class="txn-delete-form"' in body, (
        "Each transaction row must have a delete form"
    )
    assert 'class="txn-delete-btn"' in body, (
        "Each delete form must have a Delete button"
    )
    assert f'action="/expenses/{expense_id}/delete"' in body, (
        "The delete form must point at the expense's delete URL"
    )
    assert 'name="csrf_token"' in body, (
        "The delete form must carry a hidden csrf_token field"
    )


def test_no_delete_controls_when_logged_out(client):
    body = client.get("/").get_data(as_text=True)
    assert "txn-delete" not in body, "Logged-out visitors must not see delete controls"


# ------------------------------------------------------------------ #
# POST /expenses/<id>/delete — happy path                             #
# ------------------------------------------------------------------ #


def test_delete_expense_redirects_to_profile(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_delete_expense_flashes_success(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/delete",
        data={"csrf_token": "test-csrf-token"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Expense deleted." in resp.get_data(as_text=True)


def test_delete_expense_removes_row_from_db(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    assert _expense_row(expense_id) is not None
    authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    assert _expense_row(expense_id) is None, (
        "The deleted expense must be gone from the database"
    )


# ------------------------------------------------------------------ #
# Summary stats (DoD: total drops by the amount, count drops by 1)    #
# ------------------------------------------------------------------ #


def test_delete_expense_total_spent_and_count_update(authed_client, seed_id):
    """The first seeded expense is 26.79; deleting it must drop the total by
    exactly that amount and the transaction count by 1."""
    expense_id = _first_expense_id(seed_id)
    assert _expense_row(expense_id)["amount"] == 26.79

    authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    body = authed_client.get("/profile").get_data(as_text=True)
    assert f"₨{SEED_TOTAL - 26.79:,.2f}" in body, (
        "Total spent must decrease by exactly the deleted amount"
    )
    assert f">{SEED_COUNT - 1}<" in body, "Transaction count must drop by 1"
    assert f"₨26.79" not in body, (
        "The deleted amount must not appear in the transaction list"
    )


def test_delete_expense_category_breakdown_updates(authed_client, seed_id):
    """Deleting a Food expense must remove its amount from the Food total."""
    expense_id = _first_expense_id(seed_id)
    assert _expense_row(expense_id)["category"] == "Food"

    authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    conn = db.get_db()
    food_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses "
        "WHERE user_id = ? AND category = 'Food'",
        (seed_id,),
    ).fetchone()[0]
    conn.close()
    assert food_total == 32.40, (
        "Deleting the first expense must remove 26.79 from the Food category "
        "total (only the 32.40 seed row remains)"
    )


def test_delete_expense_row_gone_after_refresh(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    for _ in range(2):  # two consecutive page loads == two refreshes
        body = authed_client.get("/profile").get_data(as_text=True)
        assert "Groceries for the week" not in body
        assert "₨26.79" not in body


# ------------------------------------------------------------------ #
# Auth guards (DoD: logged-out profile visit redirects to /login)     #
# ------------------------------------------------------------------ #


def test_delete_expense_post_redirects_to_login_when_logged_out(client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert _expense_row(expense_id) is not None, (
        "Logged-out POST must not delete the expense"
    )


# ------------------------------------------------------------------ #
# Ownership (DoD: another user's or non-existent id returns 404)      #
# ------------------------------------------------------------------ #


def test_delete_expense_not_found_for_missing_id(authed_client):
    resp = authed_client.post(
        "/expenses/999999/delete", data={"csrf_token": "test-csrf-token"}
    )
    assert resp.status_code == 404


def test_delete_expense_forbidden_for_other_users_expense(authed_client, other_user_id):
    conn = db.get_db()
    row = conn.execute(
        "SELECT id FROM expenses WHERE user_id = ? LIMIT 1", (other_user_id,)
    ).fetchone()
    conn.close()
    assert row is not None

    resp = authed_client.post(
        f"/expenses/{row['id']}/delete", data={"csrf_token": "test-csrf-token"}
    )
    assert resp.status_code == 404, (
        "A logged-in user must not delete another user's expense"
    )
    assert _expense_row(row["id"]) is not None, (
        "Another user's expense must remain untouched"
    )


# ------------------------------------------------------------------ #
# GET must not delete (DoD: GET deletes nothing)                     #
# ------------------------------------------------------------------ #


def test_delete_expense_get_request_deletes_nothing(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.get(f"/expenses/{expense_id}/delete")
    assert resp.status_code == 405, "The delete route must be POST-only"
    assert _expense_row(expense_id) is not None, (
        "A GET request must not delete the expense"
    )


# ------------------------------------------------------------------ #
# CSRF (DoD: bad CSRF -> 400, nothing deleted)                       #
# ------------------------------------------------------------------ #


def test_delete_expense_csrf_token_required(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(f"/expenses/{expense_id}/delete", data={})
    assert resp.status_code == 400
    assert _expense_row(expense_id) is not None, (
        "POST without csrf_token must not delete the row"
    )


def test_delete_expense_wrong_csrf_token_rejected(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    resp = authed_client.post(
        f"/expenses/{expense_id}/delete",
        data={"csrf_token": "wrong-token"},
    )
    assert resp.status_code == 400
    assert _expense_row(expense_id) is not None, (
        "POST with a wrong csrf_token must not delete the row"
    )


# ------------------------------------------------------------------ #
# Isolation (DoD: other transactions and the user account unaffected) #
# ------------------------------------------------------------------ #


def test_delete_expense_leaves_other_rows_intact(authed_client, seed_id):
    expense_id = _first_expense_id(seed_id)
    conn = db.get_db()
    before = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (seed_id,)
    ).fetchone()[0]
    conn.close()
    assert before == SEED_COUNT

    authed_client.post(
        f"/expenses/{expense_id}/delete", data={"csrf_token": "test-csrf-token"}
    )

    conn = db.get_db()
    after = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (seed_id,)
    ).fetchone()[0]
    user_count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE id = ?", (seed_id,)
    ).fetchone()[0]
    conn.close()
    assert after == SEED_COUNT - 1, "Exactly one expense must be deleted"
    assert user_count == 1, "The user account must be unaffected by a delete"
