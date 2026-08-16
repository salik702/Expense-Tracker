# Spec: Login and Logout

## Overview
Step 3 implements user authentication flow: signing in with email and password, and signing out. The login page already exists (`login.html` with a form posting to `POST /login`), and the `logout` route is stubbed. This step wires them up: `POST /login` validates credentials against the database, sets the session, and redirects to `/` on success, or re-renders the form with an error on failure. `GET /logout` clears the session and redirects to `/`.

## Depends on
- Step 1 — Database setup. Requires the `users` table with `email` and `password_hash` columns.
- Step 2 — Registration. Assumes `app.secret_key` is set and `flask.session` works; session keys `user_id` and `email` are used.

## Routes
- `GET /login` — Render the login form. — public
- `POST /login` — Validate email/password, check against database, set session, redirect to `/`. — public
- `GET /logout` — Clear session, redirect to `/`. — authenticated

## Database changes
No database changes. Uses existing `users` table from Step 1.

## Templates
- **Create:** none
- **Modify:** none

`login.html` already exists, already extends `base.html`, and already renders the `error` context variable. No template edits are needed for this step.

## Files to change
- `app.py` — Convert the `login()` view to accept `GET` and `POST`. Add the credential-checking, session-login, and redirect logic. Convert the `logout()` stub to clear the session and redirect.
- `database/db.py` — No structural change. (May be touched only if a small `get_user_by_email()` helper is preferred; optional — inlining the `SELECT` in `app.py` is also acceptable.)

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` and `flask.session` are already available via the existing Flask + Werkzeug install.

## Rules for implementation
- No SQLAlchemy or ORMs — keep using `sqlite3` via `get_db()`.
- Parameterised queries only — every `SELECT` must use `?` placeholders; never interpolate user input into SQL.
- Password verification must use `werkzeug.security.check_password_hash` against the stored hash.
- Validate input server-side: `email` and `password` are both required; `email` must be normalized with `.strip().lower()` before lookup.
- Re-render `login.html` with an `error` message on any validation failure or wrong credentials — do not redirect. Do not pre-fill the password field.
- On successful login: store `user_id` and `email` in `flask.session`, and `redirect(url_for("landing"))`.
- On logout: clear the entire session (`session.clear()`) and `redirect(url_for("landing"))`.
- Use CSS variables — never hardcode hex values in any template or CSS.
- All templates extend `base.html` (already true for `login.html`).

## Definition of done
- `GET /login` renders the login form.
- `POST /login` with valid credentials sets the session and redirects to `/`.
- `POST /login` with a missing field re-renders the form with a visible error.
- `POST /login` with an unrecognized email re-renders the form with a visible error.
- `POST /login` with a wrong password re-renders the form with a visible error (generic message: "Invalid email or password." — do not reveal which field was wrong).
- `GET /logout` clears the session and redirects to `/`.
- After a successful login, hitting `GET /` shows the landing page and `flask.session` contains `user_id` and `email`.
- After logout, `flask.session` no longer contains `user_id` or `email`.
- The form is fully usable in both light and dark themes (no hardcoded colors introduced).
