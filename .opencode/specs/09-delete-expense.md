# Spec: Delete Expense

## Overview
Step 9 replaces the `GET /expenses/<int:id>/delete` placeholder with a working
delete flow so a logged-in user can remove their own expenses. Steps 7 and 8
completed the create and update halves of CRUD; this step finishes the "delete"
half. Deleting is a destructive action, so the route is **POST-only**, requires
a valid CSRF token, verifies the expense belongs to the current user before
deleting, and confirms via the profile page transaction list. After a
successful delete the user is redirected back to the profile page where the
summary stats, transaction list, and category breakdown immediately reflect the
removal.

## Depends on
- Step 1: Database setup (`expenses` table and `get_db()` exist)
- Step 2: Registration (users are stored in the database)
- Step 3: Login / Logout (`session["user_id"]` is set on login)
- Step 5: Backend connection (profile page renders live expense data)
- Step 7: Add Expense (`insert_expense` helper and add-expense form define the
  shared form/CSRF conventions)
- Step 8: Edit Expense (`get_expense` helper, per-row transaction actions on the
  profile page, and the CSRF-validation pattern)

## Routes
- `POST /expenses/<int:id>/delete` — delete the expense owned by the current
  user, flash a success message, redirect to the profile page — logged-in

The existing placeholder route is defined as `GET /expenses/<int:id>/delete`;
replace it with a `methods=["POST"]` handler on the same URL. The route must 404
(via `abort(404)`) when the id does not exist or belongs to a different user.
Delete is never triggered by a GET link — it is always a CSRF-protected POST
from a form on the profile page.

## Database changes
No database changes. The `expenses` table already has everything needed; delete
only removes existing rows. The `user_id` foreign key is already declared, so
deleting an expense never affects other tables.

## Templates
- **Create:** none — no new templates.
- **Modify:** `templates/profile.html`
  - Add a "Delete" action next to the existing "Edit" link in each
    recent-transactions row's `.txn-actions` cell.
  - The delete control must be a small `<form method="POST"` posting to
    `url_for('delete_expense', id=txn['id'])` with a hidden
    `csrf_token` input (`value="{{ session['csrf_token'] }}"`) and a submit
    button labelled "Delete" — never a plain `<a>` link, so the destructive
    action cannot be triggered by a GET.

## Files to change
- `app.py`
  - Replace the placeholder `delete_expense()` body with a
    `methods=["POST"]` handler:
    - Redirect to `/login` when `session.get("user_id")` is missing.
    - Validate the CSRF token (`request.form.get("csrf_token") ==
      session.get("csrf_token")`), `abort(400)` on mismatch — same pattern as
      `add_expense` and `edit_expense`.
    - Look up the expense by id and verify `expense["user_id"] ==
      session["user_id"]`; otherwise `abort(404)`.
    - Delete the row via a parameterised query, flash a success message (e.g.
      "Expense deleted."), and redirect to `url_for("profile")`.
  - Remove the `GET`-only stub route for delete.
- `templates/profile.html` — add the per-row "Delete" form (see Templates).
- `static/css/profile.css` — style the delete button in `.txn-actions` so it
  sits beside the "Edit" link with consistent spacing and a subtle danger
  treatment, using CSS variables only.
- `database/queries.py` — add a `delete_expense(id)` helper using a
  parameterised `DELETE FROM expenses WHERE id = ?` query.

## Files to create
- No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format user input into SQL
- Passwords hashed with werkzeug (no auth changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles; page-specific CSS goes in `static/css/profile.css`
- Delete must be POST-only (`methods=["POST"]`) — a GET request to the delete
  URL must not delete anything and may return 405 or 404
- CSRF token must be validated on POST (match `session["csrf_token"]`),
  `abort(400)` on mismatch — same as `add_expense` and `edit_expense`
- Authorization: an expense may only be deleted when
  `expense["user_id"] == session["user_id"]`; any other id (or a non-existent
  id) returns 404. Never delete an expense that belongs to another user
- The delete button on the profile page must be a form POST with a hidden CSRF
  token — never an `<a href>` GET link
- On success, flash a message (e.g. "Expense deleted.") and redirect to
  `url_for("profile")` — the removed expense must disappear immediately from
  the transaction list, and total spent / transaction count / category
  breakdown must update accordingly
- The `delete_expense(id)` helper must be a plain parameterised DELETE that
  takes only the expense id; ownership is enforced by the route before it is
  called

## Definition of done
- [ ] Logging in as the seed user (demo@spendly.com / demo123) and visiting the
  profile page shows a "Delete" control next to each "Edit" link in the recent
  transactions table
- [ ] Clicking "Delete" on an expense removes it, redirects to the profile
  page, flashes a success message, and the transaction no longer appears in the
  list
- [ ] After deleting, total spent on the profile page decreases by exactly the
  deleted expense's amount and the transaction count drops by 1
- [ ] If the deleted expense was in the top category, the category breakdown
  and top-category stat update to reflect the removal
- [ ] The deleted expense no longer exists in the database (verify via the
  database) and is still gone after a page refresh
- [ ] Deleting an expense that belongs to another user (or a non-existent id)
  returns a 404 page, not a 500, and nothing is deleted
- [ ] Visiting `/expenses/<id>/delete` directly with a GET request deletes
  nothing (no route or 405/404), and the expense still exists
- [ ] Submitting the delete form without a valid CSRF token returns a 400 and
  the expense is not deleted
- [ ] Visiting the profile page while logged out redirects to `/login`
- [ ] All other transactions belonging to the user (and the user account) are
  unaffected by a single delete