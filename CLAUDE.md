# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**Spendly** — a personal expense-tracking Flask web app branded with a warm editorial aesthetic (DM Serif Display + DM Sans, deep-green accent). The project is a structured learning exercise: a sequence of numbered "Steps" that progressively fill in the placeholder routes in `app.py`. The landing/login/register/legal pages are already built; auth, the database, and the expense CRUD flows are the work to come.

## Run / develop

- Python: **3.13** (pinned in `.python-version`).
- Dep manager: **uv** (see `uv.lock`). The local interpreter lives in `.venv/`.
- App: single entry point `app.py` — debug server on **port 5001**.
  - `python app.py` (or `.venv/Scripts/python.exe app.py` on Windows).
- Tests: `pytest` is in `pyproject.toml` deps along with `pytest-flask`. The harness is there but no test files exist yet — when you add the first one, follow `pytest-flask` conventions (it provides a `client` fixture and `live_server`).

There is no separate `requirements.txt` — `pyproject.toml` + `uv.lock` is the source of truth.

## Architecture

A deliberately small, single-module Flask app — the entire routing layer lives in `app.py`. The shape of the codebase is the shape of the upcoming steps:

```
app.py               # Flask app + ALL routes (implemented + placeholders)
pyproject.toml       # flask 3.1.3, werkzeug 3.1.6, pytest 8.3.5, pytest-flask 1.3.0
.python-version      # 3.13
database/
  __init__.py
  db.py              # students implement: get_db(), init_db(), seed_db()
templates/
  base.html          # layout: navbar, footer, theme bootstrap, theme-toggle button
  landing.html       # marketing landing page (hero, features, CTA, YouTube demo modal)
  login.html         # sign-in form (POST /login route not yet implemented)
  register.html      # sign-up form (POST /register route not yet implemented)
  terms.html         # legal — Terms and Conditions
  privacy.html       # legal — Privacy Policy
static/
  css/
    style.css        # design tokens (light + dark), global layout, forms, modal
    landing.css      # landing-only styles (hero, features, CTA, mock dashboard)
  js/
    main.js          # shared: light/dark theme toggle (localStorage + prefers-color-scheme)
```

`database/db.py` is a stub with the three functions it expects (`get_db`, `init_db`, `seed_db`) and a comment block describing the contract — when implementing, mirror that contract. The repo's `.gitignore` already excludes `expense_tracker.db` and `__pycache__/`, so the SQLite file is intentionally ephemeral.

## Routes in `app.py`

Two groups:

1. **Live routes** — `GET /` (landing), `GET /register`, `GET /login`, `GET /terms`, `GET /privacy`. These render templates today; the corresponding `POST` handlers (and the form-submission logic) are part of upcoming steps.
2. **Placeholder routes** — `GET /logout`, `GET /profile`, `GET /expenses/add`, `GET /expenses/<int:id>/edit`, `GET /expenses/<int:id>/delete`. Each returns a plain string noting which step will implement it (Steps 3, 4, 7, 8, 9 respectively). When filling these in, the URL signatures are already fixed — match them.

## Frontend conventions worth knowing before you touch templates or CSS

- All pages extend `templates/base.html`. The base template pre-paints the theme before first paint via an inline `<script>` to avoid a light/dark flash; keep that script intact when editing `<head>`.
- Theme tokens are CSS custom properties on `:root` with a dark override block in `static/css/style.css`. **Add new colors as tokens, not as one-off hex values** — both `style.css` and `landing.css` consume them.
- The theme is persisted in `localStorage` under the key `spendly-theme` (values: `'light'` | `'dark'`). The toggle button is `.theme-toggle` with `data-theme-toggle` — `main.js` wires it up. If you add new components that need to react to the theme, listen for the same toggle pattern rather than re-reading storage.
- The landing page embeds a YouTube demo modal (`#demo-modal`) opened by `[data-open-demo]` and closed by `[data-close-demo]`. The `src` is blanked on close so the video stops — preserve that behavior.
- Forms (`login.html`, `register.html`) already expect an `error` context variable for `auth-error` rendering. The `POST` handlers in upcoming steps should pass `error=` on failure and re-render the same template.
- The navbar's "Get started" button links to `register`; the brand links to `landing`. Footer links to `/terms` and `/privacy` are hard-coded paths (not `url_for`), to match the rest of the legal-style static text.

## Local config

`.claude/settings.local.json` configures this harness to talk to a local Ollama instance at `http://localhost:11434` (env vars `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN=ollama`, `ANTHROPIC_MODEL=minimax-m3:cloud`) and pre-allowlists `Bash(dir /b templates static)` and `Bash(.venv/Scripts/python.exe *)`. Don't rely on a different Python — the venv interpreter is the whitelisted one.
