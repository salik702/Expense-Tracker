# Spec: Registration

## Overview
Step 2 wires up the registration flow so a new visitor can create a Spendly account. The `register.html` template is already in place with a form posting to `POST /register`; this step adds the handler that validates the input, hashes the password, inserts a `users` row, signs the user in, and redirects them into the app. Email uniqueness is enforced by the `users` table from Step 1 (`email NOT NULL UNIQUE`); duplicate registrations surface as a friendly error and the same form is re-rendered.

## Depends on
- Step 1 — Database setup. Requires the `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) and the `get_db()` helper in `database/db.py`.

## Routes
- `POST /register` — Validate form input, hash the password, insert the user, log them in, redirect to `/`. — public

No new routes are added; the existing `GET /register` route stays unchanged.

## Database changes
No database changes. The `users` table and its `email` UNIQUE constraint already exist from Step 1. `password_hash` storage uses the `TEXT` column already present.

## Templates
- **Create:** none
- **Modify:** none

`register.html` already exists, already extends `base.html`, and already renders the `error` context variable. No template edits are needed for this step.

## Files to change
- `app.py` — Convert the `register()` view to accept `GET` and `POST`. Add the validation, insert, and session-login logic. Set `app.secret_key` so Flask's `session` works.
- `database/db.py` — No structural change. (May be touched only if a small `create_user()` helper is preferred; optional — inlining the `INSERT` in `app.py` is also acceptable.)

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` and `flask.session` are already available via the existing Flask + Werkzeug install.

## Rules for implementation
- No SQLAlchemy or ORMs — keep using `sqlite3` via `get_db()`.
- Parameterised queries only — every `INSERT` / `SELECT` must use `?` placeholders; never interpolate user input into SQL.
- Passwords must be hashed with `werkzeug.security.generate_password_hash` before storage. Never store or log plaintext passwords.
- Validate input server-side: `name`, `email`, and `password` are all required; `email` must look like an email (a simple `@` check is sufficient for this learning step); `password` must be at least 8 characters (matches the placeholder hint in `register.html`).
- Re-render `register.html` with an `error` message on any validation failure or duplicate email — do not redirect. Preserve the form state by re-filling `name` and `email` (not `password`) on re-render.
- On success: insert the user, store `user_id` and `email` in `flask.session`, and `redirect(url_for("landing"))`.
- Set `app.secret_key` to a stable value loaded from an environment variable with a development fallback (e.g. `os.environ.get("SPENDLY_SECRET_KEY", "dev-secret-change-me")`). Do not commit a real production secret.
- Use CSS variables — never hardcode hex values in any new template or CSS.
- All templates extend `base.html` (already true for `register.html`).
- Email comparisons for duplicate detection must be case-insensitive — normalize with `email.strip().lower()` before insert and before checking.

## Definition of done
- `GET /register` still renders the registration form.
- `POST /register` with valid input creates a row in the `users` table, sets the session, and redirects to `/`.
- `POST /register` with a missing field re-renders the form with a visible error and no row is inserted.
- `POST /register` with `password` shorter than 8 characters re-renders the form with a visible error and no row is inserted.
- `POST /register` with an already-registered email re-renders the form with a visible error and no row is inserted.
- The `users.password_hash` column never contains a plaintext password (verify with a quick DB query after a test registration).
- After a successful registration, hitting `GET /` shows the landing page and `flask.session` contains the new `user_id`.
- The form is fully usable in both light and dark themes (no hardcoded colors introduced).
