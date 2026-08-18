# Spec: Add Expense

## Overview
Step 7 fills in the `GET /expenses/add` placeholder route and adds the matching
`POST /expenses/add` handler so a logged-in user can record a new expense. The
expenses table, auth, and profile page already exist; the profile page reads
live data, but there is currently no way to create a new row. This step adds a
single-page form (amount, category, date, optional description), validates the
submission server-side, inserts the row via a parameterised query, and
redirects back to the profile page where the new expense immediately appears in
the summary stats, transaction list, and category breakdown.

## Depends on
- Step 1: Database setup (`expenses` table and `get_db()` exist)
- Step 2: Registration (users are stored in the database)
- Step 3: Login / Logout (`session["user_id"]` is set on login)
- Step 5: Backend connection (profile page renders live expense data)

## Routes
- `GET /expenses/add` — render the "Add expense" form — logged-in
- `POST /expenses/add` — validate the submitted form, insert the expense,
  redirect to the profile page — logged-in

Both methods live on the existing `add_expense()` view function. The URL
signature `GET /expenses/add` is already fixed by the placeholder — match it.

## Database changes
No database changes. The `expenses` table already has every column needed:
`user_id`, `amount` (REAL), `category` (TEXT), `date` (TEXT, `YYYY-MM-DD`),
`description` (TEXT, nullable), `created_at`.

## Templates
- **Create**: `templates/add_expense.html`
  - Extends `base.html`; extends the existing `.auth-section` / `.auth-container`
    / `.auth-card` form styling used by `login.html` and `register.html`
    (centered single-column card).
  - Renders an `error` context variable as a `.auth-error` banner when present,
    and pre-fills submitted values (amount, category, date, description) on
    validation failure.
  - Fields:
    - Amount — `<input type="number" name="amount" min="0.01" step="0.01">`
      with a ₹ prefix
    - Category — `<select name="category">` populated from the `CATEGORIES`
      list passed in from `app.py`; no "please pick" empty option required, but
      the first option is selected by default
    - Date — `<input type="date" name="date">`
    - Description — optional `<input type="text" name="description">`
    - Submit button "Add expense"
  - Category badges reuse the existing `.category-badge` / `--cat-*` token
    classes where a selected-category preview is shown.
- **Modify**: `templates/base.html`
  - Add an "Add expense" nav link for logged-in users, using `url_for('add_expense')`
    and the same `.is-active` pattern already used for the profile/analytics links.
- **Modify**: `templates/profile.html`
  - Add an "Add expense" link/button in the filter bar area pointing at
    `url_for('add_expense')` so the new page is reachable from the dashboard.

## Files to change
- `app.py`
  - Replace the placeholder `add_expense()` body with a `methods=["GET", "POST"]`
    handler:
    - Redirect to `/login` when `session.get("user_id")` is missing.
    - `GET` — render `add_expense.html` with the category list.
    - `POST` — validate, insert, redirect to `url_for("profile")` with a
      success flash message; on failure re-render the form with `error=` and the
      submitted values.
  - Import `CATEGORIES` from `database.db` and pass it to the template.
- `templates/base.html` — add the "Add expense" nav link (see Templates).
- `templates/profile.html` — add the "Add expense" button (see Templates).
- `static/css/add_expense.css` — new stylesheet for the form page (see Files to create).

## Files to create
- `templates/add_expense.html`
- `static/css/add_expense.css`
  - Styles for the add-expense form page using CSS variables only: the form
    grid/stack layout, the ₹ amount prefix, focus states, and a
    category-selector treatment consistent with the existing category tokens.
    Page-specific stylesheet linked via `{% block head %}` like `profile.css`.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format user input into SQL
- Passwords hashed with werkzeug (no auth changes in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles; page-specific CSS goes in `static/css/add_expense.css`
- Currency must always display as ₹
- Amount validation: must be present, parseable as a number, and greater than 0;
  otherwise re-render with a user-facing error
- Category validation: must be one of the entries in `CATEGORIES` (server-side
  allowlist, not just the select's options)
- Date validation: must match `YYYY-MM-DD` (reuse `_parse_date` from `app.py`);
  otherwise re-render with a user-facing error
- Description is optional; empty string must be stored as `NULL`
- On success, flash a message (e.g. "Expense added.") and redirect to
  `url_for("profile")` — the new expense must appear immediately on the profile
  page
- The form must pre-fill submitted values on validation failure (never wipe the
  user's input)
- `insert` must bind `user_id` from `session["user_id"]` — never from the form
- Category options in the template come from the `CATEGORIES` list passed in by
  the route — never hardcoded in the template

## Definition of done
- [ ] Logging in as the seed user (demo@spendly.com / demo123) and visiting
  `/expenses/add` shows the expense form with an amount field, a category
  dropdown listing all 7 categories, a date field, and a description field
- [ ] Submitting a valid expense (amount, category, date) redirects to the
  profile page and flashes a success message
- [ ] After submission, the profile page's transaction list shows the new
  expense as the newest row with the correct amount (₹) and category
- [ ] Total spent on the profile page increases by exactly the entered amount
- [ ] Transaction count on the profile page increments by 1
- [ ] Submitting an empty or non-numeric amount shows an error on the form and
  does not insert a row
- [ ] Submitting an amount of 0 or negative shows an error on the form and does
  not insert a row
- [ ] Submitting an invalid date shows an error on the form and does not insert
  a row
- [ ] Submitting a category not in the list shows an error on the form and does
  not insert a row
- [ ] On validation failure the previously entered values remain filled in the
  form
- [ ] Submitting with a blank description stores `NULL` and the expense still
  appears on the profile page (empty description cell)
- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] The "Add expense" link is visible in the navbar for logged-in users and
  on the profile page
- [ ] The new expense persists after a page refresh and appears in the database