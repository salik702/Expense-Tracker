# Spec: Edit Expense

## Overview
Step 8 fills in the `GET /expenses/<int:id>/edit` placeholder route and adds the
matching `POST /expenses/<int:id>/edit` handler so a logged-in user can update
an existing expense. Step 7 added the ability to create expenses; this step
completes the "update" half of CRUD by letting a user correct a mistake (wrong
amount, category, date, or description) on any of their own expenses. The edit
form reuses the same fields and validation rules as the add-expense form, is
pre-filled with the stored values, and only ever touches the current user's rows.
After a successful save the user is redirected back to the profile page where the
updated expense immediately reflects in the summary stats, transaction list, and
category breakdown.

## Depends on
- Step 1: Database setup (`expenses` table and `get_db()` exist)
- Step 2: Registration (users are stored in the database)
- Step 3: Login / Logout (`session["user_id"]` is set on login)
- Step 5: Backend connection (profile page renders live expense data)
- Step 7: Add Expense (`insert_expense` helper and add-expense form exist and
  define the shared field/validation conventions)

## Routes
- `GET /expenses/<int:id>/edit` — render the "Edit expense" form pre-filled
  with the expense's current values — logged-in
- `POST /expenses/<int:id>/edit` — validate the submitted form, update the
  expense, redirect to the profile page — logged-in

Both methods live on the existing `edit_expense()` view function. The URL
signature `GET /expenses/<int:id>/edit` is already fixed by the placeholder —
match it. The route must 404 (via `abort(404)`) when the id does not exist or
belongs to a different user.

## Database changes
No database changes. The `expenses` table already has every column needed:
`user_id`, `amount` (REAL), `category` (TEXT), `date` (TEXT, `YYYY-MM-DD`),
`description` (TEXT, nullable), `created_at`. Editing only updates existing
columns on existing rows; `created_at` is preserved.

## Templates
- **Create**: `templates/edit_expense.html`
  - Extends `base.html`; same structure and styling approach as
    `add_expense.html` (extends `.auth-section` / `.auth-container` /
    `.auth-card`, centered single-column card).
  - Renders an `error` context variable as a `.auth-error` banner when present,
    and pre-fills values (amount, category, date, description) from the expense
    on GET and from the submitted form on validation failure.
  - Fields (identical to add-expense):
    - Amount — `<input type="number" name="amount" min="0.01" step="0.01">`
      with a ₨ prefix
    - Category — `<select name="category">` populated from the `CATEGORIES`
      list; the expense's current category is pre-selected
    - Date — `<input type="date" name="date">` pre-filled with the stored date
    - Description — optional `<input type="text" name="description">`
    - Submit button "Save changes"
  - Form posts to `url_for('edit_expense', id=expense['id'])` and includes the
    CSRF token hidden field, matching `add_expense.html`.
  - Page title "Edit expense — Spendly".
- **Modify**: `templates/profile.html`
  - Add an "Edit" link for each transaction row in the recent-transactions
    table, pointing at `url_for('edit_expense', id=txn['id'])`.
  - This requires the transaction dicts to include an `id` (see app.py changes).

## Files to change
- `app.py`
  - Replace the placeholder `edit_expense()` body with a
    `methods=["GET", "POST"]` handler:
    - Redirect to `/login` when `session.get("user_id")` is missing.
    - Look up the expense by id and verify `expense["user_id"] ==
      session["user_id"]`; otherwise `abort(404)`.
    - `GET` — render `edit_expense.html` with the expense's values and the
      category list.
    - `POST` — validate (same rules as add expense), update the row via a
      parameterised query, flash a success message, redirect to
      `url_for("profile")`; on failure re-render the form with `error=` and the
      submitted values.
  - Add a `get_expense(id)` helper (in `database/queries.py`) that returns the
    row as a dict, or None when missing.
  - Add an `update_expense(id, amount, category, date, description)` helper (in
    `database/queries.py`) using a parameterised `UPDATE` query.
  - Include `id` in the transaction dicts returned by
    `get_recent_transactions` (SELECT `id` and carry it through) so the profile
    template can render edit links.
- `templates/profile.html` — add the per-row "Edit" link (see Templates).
- `database/queries.py` — add `get_expense`, `update_expense`, and the `id`
  field in `get_recent_transactions`.
- `static/css/edit_expense.css` — new stylesheet (see Files to create).

## Files to create
- `templates/edit_expense.html`
- `static/css/edit_expense.css`
  - Reuses the same amount-prefix and form-hint styles as `add_expense.css`.
    Only add anything page-specific here; do not duplicate `add_expense.css`
    wholesale if the shared rules can be reused. Use CSS variables only.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format user input into SQL
- Passwords hashed with werkzeug (no auth changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles; page-specific CSS goes in `static/css/edit_expense.css`
- Currency must always display as ₨
- Amount validation: must be present, parseable as a number, and greater than 0;
  otherwise re-render with a user-facing error
- Category validation: must be one of the entries in `CATEGORIES` (server-side
  allowlist, not just the select's options)
- Date validation: must match `YYYY-MM-DD` (reuse `_parse_date` from `app.py`);
  otherwise re-render with a user-facing error
- Description is optional; empty string must be stored as `NULL`
- CSRF token must be validated on POST (match `session["csrf_token"]`),
  `abort(400)` on mismatch — same as `add_expense`
- Authorization: an expense may only be edited when
  `expense["user_id"] == session["user_id"]`; any other id returns 404. Never
  update an expense that belongs to another user
- The route must bind `user_id` into the WHERE clause of the UPDATE — never trust
  the expense id from the form alone; always re-check ownership
- On success, flash a message (e.g. "Expense updated.") and redirect to
  `url_for("profile")` — the updated values must appear immediately on the
  profile page
- The form must pre-fill current values on GET and submitted values on
  validation failure (never wipe the user's input)
- Category options in the template come from the `CATEGORIES` list passed in by
  the route — never hardcoded in the template
- `created_at` must never be overwritten by an update

## Definition of done
- [ ] Logging in as the seed user (demo@spendly.com / demo123), visiting the
  profile page, and clicking "Edit" on a transaction opens the edit form
  pre-filled with that expense's amount, category, date, and description
- [ ] `GET /expenses/<id>/edit` for a valid, owned expense shows "Edit expense"
  as the title and a "Save changes" submit button
- [ ] Changing the amount and saving redirects to the profile page, flashes a
  success message, and shows the new amount (₨) in the transaction list
- [ ] Total spent on the profile page changes by exactly the difference between
  the old and new amounts
- [ ] Changing the category and saving reflects the new category badge on the
  transaction and the category breakdown
- [ ] Editing an expense and saving with a blank description stores `NULL` and
  the transaction still appears
- [ ] Submitting an empty, non-numeric, zero, or negative amount shows an error
  on the form and does not update the row
- [ ] Submitting an invalid date shows an error on the form and does not update
  the row
- [ ] Submitting a category not in the list shows an error on the form and does
  not update the row
- [ ] On validation failure the previously entered values remain filled in the
  form
- [ ] Editing an expense that belongs to another user (or a non-existent id)
  returns a 404 page, not a 500 or a form
- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`
- [ ] `created_at` of the edited expense is unchanged (verify via the database)
- [ ] The updated values persist after a page refresh and appear in the database