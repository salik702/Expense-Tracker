<div align="center">

<!-- Header Banner — Cylinder style, cyan/electric theme -->
<img src="https://capsule-render.vercel.app/api?type=shark&color=0:020817,40:0c1a3a,70:0e3a6e,100:020817&height=230&section=header&text=SPENDLY%20EXPENSE%20TRACKER&fontSize=58&fontColor=ffffff&animation=fadeIn&fontAlignY=45&desc=Track%20Every%20Rupee%20%7C%20Know%20Where%20It%20Goes&descAlignY=68&descSize=17&descColor=67e8f9" width="100%"/>

<br/>

<!-- Header Typing Animation -->
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=800&size=21&duration=2800&pause=800&color=22D3EE&center=true&vCenter=true&repeat=true&width=880&height=52&lines=Track+your+expenses+effortlessly;Add+category%2C+amount%2C+date+and+description;View+spending+patterns+and+monthly+summaries;Filter+by+time+period+and+compare+data" alt="Typing SVG" />

<br/><br/>

<!-- Badge Row 1 -->
<p>
  <img src="https://img.shields.io/badge/PROJECT-Spendly%20Expense%20Tracker-0ea5e9?style=for-the-badge&logo=bookstack&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/FRAMEWORK-Flask%203.1%20%2B%20Jinja2-61DAFB?style=for-the-badge&logo=flask&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/LANGUAGE-Python%203.13-F7DF1E?style=for-the-badge&logo=python&logoColor=black&labelColor=020817" />
  <img src="https://img.shields.io/badge/STATUS-Active-22c55e?style=for-the-badge&logo=github&logoColor=white&labelColor=020817" />
</p>

<!-- Badge Row 2 -->
<p>
  <img src="https://img.shields.io/badge/DATABASE-SQLite-22d3ee?style=for-the-badge&logo=sqlite&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/STYLING-Custom%20CSS%20%2B%20Design%20Tokens-f97316?style=for-the-badge&logo=css3&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/SECURITY-CSRF%20%2B%20Werkzeug%20Hashing-f59e0b?style=for-the-badge&logo=security&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/TESTING-pytest%20%2B%20pytest--flask-16a34a?style=for-the-badge&logo=pytest&logoColor=white&labelColor=020817" />
</p>

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== TABLE OF CONTENTS ===================== -->

## `> INDEX.NAVIGATION — TABLE OF CONTENTS`

| `#` | `SECTION` | `LINK` |
| :-: | :-------- | :----- |
| 01 | About the Project | [`PROJECT.ABOUT`](#-projectabout--what-is-spendly) |
| 02 | Feature Overview | [`FEATURES.DECK`](#-featuresdeck--key-capabilities) |
| 03 | Technology Stack | [`STACK.LOAD`](#-stackload--technologies) |
| 04 | Repository Layout | [`PROJECT.STRUCTURE`](#-projectstructure--repo-layout) |
| 05 | Quickstart | [`QUICKSTART.SETUP`](#-quickstartsetup--get-running-in-5-minutes) |
| 06 | Development Guide | [`DEV.WORKFLOW`](#-devworkflow--tests--commands) |
| 07 | API Surface | [`ROUTES.MAP`](#-routesmap--available-endpoints) |
| 08 | Security & Data | [`SECURITY.MODEL`](#-securitymodel--sessions-csrf--data) |
| 09 | Roadmap | [`ROADMAP`](#-roadmap--future-work) |
| 10 | Contribution Guide | [`CONTRIBUTION.PROTOCOL`](#-contributionprotocol--how-to-help) |
| 11 | Visual Identity | [`DESIGN.AESTHETIC`](#-designaesthetic--visual-identity) |
| 12 | License & Support | [`SUPPORT.LICENSE`](#-supportlicense--star--report--follow) |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 01. ABOUT ===================== -->

## `> PROJECT.ABOUT — WHAT IS SPENDLY?`

**Spendly** is a personal expense tracking web application built with **Flask**. It helps you log expenses, spot spending patterns, and stay on budget — without the spreadsheet headache.

Users can register, sign in, add expenses with **category, amount, date, and description**, then visualise their spending through **category breakdowns**, **monthly summaries**, and **date-range filters** on a personal profile dashboard.

Built with **Flask + Jinja2** for server-side rendering, **SQLite** for zero-config storage, and **custom CSS** with design tokens for a warm editorial aesthetic. Features automatic dark/light theme detection with a manual toggle, CSRF-protected forms, and Werkzeug password hashing.

### Why Spendly?

| `PROBLEM` | `SOLUTION` |
| :-------- | :--------- |
| Spreadsheets are tedious and error-prone | One-click expense logging with structured fields |
| No insight into spending habits | Category breakdowns, recent transactions, and date filtering |
| Complex finance apps are overkill | A clean, focused, personal tracker |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 02. FEATURES ===================== -->

## `> FEATURES.DECK — KEY CAPABILITIES`

<div align="center">

| `FEATURE` | `DESCRIPTION` | `STATUS` |
| :-------: | :------------ | :------: |
| 🔐 User Accounts | Register, sign in, sign out with Werkzeug-hashed passwords | `✅ LIVE` |
| 💰 Log Expenses | Add any expense in seconds with all details | `✅ LIVE` |
| ✏️ Edit Expenses | Update any field of an existing expense | `✅ LIVE` |
| 🗑️ Delete Expenses | Remove expenses with CSRF-protected POST | `✅ LIVE` |
| � Category Breakdown | Per-category totals and share of spending | `✅ LIVE` |
| 📈 Profile Dashboard | Summary stats, recent transactions, category cards | `✅ LIVE` |
| 🗓️ Date Filtering | Preset ranges (this month, 3 months, 6 months) + custom range | `✅ LIVE` |
| 📊 Analytics Page | Dedicated analytics view | `✅ LIVE` |
| 🛡️ CSRF Protection | Token-based form protection on every state-changing request | `✅ LIVE` |
| 🌓 Theme Support | Automatic dark/light detection + manual toggle | `✅ LIVE` |
| 📱 Responsive Design | Works on desktop and mobile devices | `✅ LIVE` |
| 🧪 Test Suite | pytest + pytest-flask covering every shipped feature | `✅ LIVE` |

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 03. STACK ===================== -->

## `> STACK.LOAD — TECHNOLOGIES`

<div align="center">

<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/Jinja2-B4418D?style=for-the-badge&logo=jinja&logoColor=white" />
<img src="https://img.shields.io/badge/Werkzeug-B71C1C?style=for-the-badge&logo=security&logoColor=white" />
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
<img src="https://img.shields.io/badge/UV-3B82F6?style=for-the-badge&logo=uv&logoColor=white" />
<img src="https://img.shields.io/badge/pytest-16a34a?style=for-the-badge&logo=pytest&logoColor=white" />

</div>

| `LAYER` | `TECHNOLOGY` | `PURPOSE` |
| :------ | :----------- | :-------- |
| Backend | Flask 3.1.3 / Werkzeug 3.1.6 | Routing, sessions, password hashing |
| Language | Python 3.13 | Core application logic |
| Storage | SQLite (stdlib `sqlite3`) | Local, zero-config database |
| Templating | Jinja2 | Dynamic HTML generation |
| Forms | CSRF tokens + `flask.session` | Cross-site request forgery protection |
| Frontend | CSS3 + vanilla JS | Design tokens, theme toggle |
| Testing | pytest 8.3.5 + pytest-flask 1.3.0 | Feature-level integration tests |
| Tooling | uv | Dependency + environment management |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 04. STRUCTURE ===================== -->

## `> PROJECT.STRUCTURE — REPO LAYOUT`

```text
expense-tracker/
├── app.py                          ← Flask app, all routes, CSRF middleware
├── pyproject.toml                  ← Project metadata + dependencies
├── uv.lock                         ← uv lockfile for reproducible installs
├── .python-version                 ← Python version pin (3.13)
├── opencode.json                   ← OpenCode agent/command config
│
├── database/
│   ├── __init__.py
│   ├── db.py                       ← init_db, seed_db, CATEGORIES, get_db
│   └── queries.py                  ← CRUD + analytics SQL helpers
│
├── static/
│   ├── css/
│   │   ├── style.css               ← Global styles + design tokens
│   │   └── landing.css             ← Landing page styles
│   └── js/
│       └── main.js                 ← Theme toggle + shared JS
│
├── templates/
│   ├── base.html                   ← Shared navbar + footer
│   ├── landing.html                ← Marketing landing page
│   ├── register.html               ← Registration form
│   ├── login.html                  ← Sign-in form
│   ├── profile.html                ← User dashboard (stats, transactions, categories)
│   ├── analytics.html              ← Analytics view
│   ├── add_expense.html            ← Create-expense form (CSRF)
│   ├── edit_expense.html           ← Edit-expense form (CSRF)
│   ├── terms.html                  ← Terms and Conditions
│   └── privacy.html                ← Privacy Policy
│
├── tests/
│   ├── test_backend_connection.py  ← Smoke tests for the app boot
│   ├── test_date_filter.py         ← Profile date-filter helpers
│   ├── test_06-date-filter-profile.py
│   ├── test_07-add-expense.py      ← Add-expense flow (validation, CSRF, DB)
│   ├── test_08-edit-expense.py     ← Edit-expense flow (ownership, validation)
│   └── test_09-delete-expense.py   ← Delete-expense flow (CSRF, ownership)
│
├── seed_user.py                    ← Seed a demo user
├── seed_expenses.py                ← Seed demo expenses
└── expense_tracker.db              ← Local SQLite database (gitignored)
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 05. QUICKSTART ===================== -->

## `> QUICKSTART.SETUP — GET RUNNING IN 5 MINUTES`

### Prerequisites

- **Python 3.13** — pinned via `.python-version`
- **uv** — fast dependency manager (recommended)

### Option A — With uv (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/SalikAhmad702/expense-tracker.git
cd expense-tracker

# 2. Create venv and install dependencies
uv sync

# 3. Start the development server
python app.py
```

The database is initialised and seeded automatically on app boot — no manual step required.

### Option B — With pip

```bash
# 1. Clone the repo
git clone https://github.com/SalikAhmad702/expense-tracker.git
cd expense-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Start the development server
python app.py
```

<div align="center">

> **Open `http://localhost:5001` in your browser 🎉**

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 06. DEVELOPMENT ===================== -->

## `> DEV.WORKFLOW — TESTS & COMMANDS`

| `TASK` | `COMMAND` |
| :----- | :-------- |
| Run the app | `python app.py` |
| Run the full test suite | `pytest` |
| Run a single test file | `pytest tests/test_07-add-expense.py` |
| Initialise the database only | `python -c "from database.db import init_db; init_db()"` |
| Seed the database only | `python -c "from database.db import seed_db; seed_db()"` |
| Seed a demo user | `python seed_user.py` |
| Seed demo expenses | `python seed_expenses.py` |
| Sync dependencies | `uv sync` |
| Lint / format (via opencode) | configured in `opencode.json` |

> 💡 `app.py` calls `init_db()` and `seed_db()` on startup, so the database is ready the first time you boot the server.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 07. ROUTES ===================== -->

## `> ROUTES.MAP — AVAILABLE ENDPOINTS`

<div align="center">

| `ROUTE` | `METHOD` | `DESCRIPTION` | `STATUS` |
| :------ | :------: | :------------ | :------: |
| `/` | GET | Landing page | `✅ ACTIVE` |
| `/register` | GET, POST | Create an account | `✅ ACTIVE` |
| `/login` | GET, POST | Sign in | `✅ ACTIVE` |
| `/logout` | GET | Sign out and clear session | `✅ ACTIVE` |
| `/profile` | GET | User dashboard (stats, transactions, categories, filters) | `✅ ACTIVE` |
| `/analytics` | GET | Analytics view | `✅ ACTIVE` |
| `/expenses/add` | GET, POST | Add a new expense (CSRF) | `✅ ACTIVE` |
| `/expenses/<int:id>/edit` | GET, POST | Edit an existing expense (CSRF) | `✅ ACTIVE` |
| `/expenses/<int:id>/delete` | POST | Delete an expense (CSRF) | `✅ ACTIVE` |
| `/terms` | GET | Terms and Conditions | `✅ ACTIVE` |
| `/privacy` | GET | Privacy Policy | `✅ ACTIVE` |

</div>

All mutating endpoints are gated by `@app.before_request` CSRF middleware and require a signed-in user (except `/register` and `/login`). Expense endpoints enforce ownership — a user can only see and mutate their own rows.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 08. SECURITY ===================== -->

## `> SECURITY.MODEL — SESSIONS, CSRF & DATA`

Spendly takes a pragmatic, dependency-light approach to security:

| `CONCERN` | `MITIGATION` |
| :-------- | :----------- |
| Password storage | `werkzeug.security.generate_password_hash` (PBKDF2 by default) |
| Password verification | Constant-time `check_password_hash` on login |
| Session integrity | Flask's signed `session` cookie; `SECRET_KEY` read from `SPENDLY_SECRET_KEY` env var |
| CSRF | Per-session token generated by `@app.before_request`; validated on every POST |
| Cookie scope | `SESSION_COOKIE_SAMESITE = "Lax"` |
| Authorisation | Expense routes check `expense.user_id == session["user_id"]` and `404` otherwise |
| Input validation | Server-side checks on amount (`> 0`, finite), date (`YYYY-MM-DD`), category (allow-list), description (`≤ 200` chars) |

> 🔐 **In production**, set `SPENDLY_SECRET_KEY` to a long random value and run behind HTTPS.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 09. ROADMAP ===================== -->

## `> ROADMAP — FUTURE WORK`

### Shipped in v0.1 ✅

- [x] User registration, login, logout with password hashing
- [x] Personal profile dashboard (stats, transactions, categories)
- [x] Add / edit / delete expenses with CSRF protection
- [x] Date filtering with presets + custom range
- [x] Analytics view
- [x] Dark / light theme with manual toggle
- [x] pytest + pytest-flask test suite per feature

### Next up

- [ ] CSV / Excel export of expenses
- [ ] Search across expense descriptions
- [ ] Monthly budget caps with progress bars
- [ ] Chart.js visualisations on the analytics page
- [ ] Password reset flow
- [ ] Email verification on registration

### Quality of life

- [ ] Pagination on the transactions list
- [ ] Bulk delete
- [ ] Receipt attachments
- [ ] Recurring-expense templates

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 10. CONTRIBUTING ===================== -->

## `> CONTRIBUTION.PROTOCOL — HOW TO HELP`

### Quick workflow

```bash
# Fork → Branch → Commit → Push → PR
git checkout -b feature/your-improvement
git add .
git commit -m "feat: describe your change"
git push origin feature/your-improvement
```

### Guidelines

- ✅ Follow the existing code style
- ✅ Describe what your PR changes and why
- ✅ Keep commits focused and atomic
- 🧪 Run `pytest` before opening a PR — every shipped feature has a matching test file

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 11. DESIGN ===================== -->

## `> DESIGN.AESTHETIC — VISUAL IDENTITY`

Spendly uses a **warm editorial aesthetic** with:

| `ELEMENT` | `DETAILS` |
| :-------- | :-------- |
| 🎨 Color Palette | Deep green accent (#1a472a), warm paper tones (#f7f6f3) |
| ✍️ Typography | DM Serif Display for headings, DM Sans for body text |
| 🌗 Theme Support | Automatic dark/light mode detection + manual override |
| 🔷 Icons | Custom CSS icons with geometric shapes |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<!-- ===================== 12. LICENSE & SUPPORT ===================== -->

## `> SUPPORT.LICENSE — STAR · REPORT · FOLLOW`

> **License:** This project is currently **unlicensed** — no formal license file yet. Please reach out before using it commercially.

Found a bug? Have a feature idea? Open an **Issue** on GitHub — every report makes Spendly better.

If this project helped you with expense tracking or Flask development, consider giving it a ⭐ — it keeps the development going!

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<div align="center">

<!-- Footer Waving Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:020817,40:0c1a3a,70:0e3a6e,100:020817&height=200&section=footer&text=SALIK%20AHMAD&fontSize=52&fontColor=ffffff&animation=twinkling&fontAlignY=45&desc=AI%2FML%20Engineer&descAlignY=68&descSize=16&descColor=67e8f9" width="100%"/>

<br/>

<!-- Footer Typing -->
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=15&duration=3200&pause=1000&color=22D3EE&center=true&vCenter=true&repeat=true&width=860&height=42&lines=Track+every+rupee.+Own+your+finances.;Add+expenses.+See+patterns.+Stay+on+budget.;Built+with+Flask+and+Python+3.13;Visit+salikahmad.vercel.app" alt="Footer Typing" />

<br/><br/>

<!-- Skill Capsule -->
<img src="https://capsule-render.vercel.app/api?type=soft&color=0:020817,100:0e3a6e&height=58&text=Flask%20%7C%20Python%20%7C%20SQLite%20%7C%20Jinja2%20%7C%20Werkzeug%20%7C%20pytest&fontSize=16&fontColor=67e8f9&animation=fadeIn" width="80%" />

<br/><br/>

<!-- Social Links -->
<a href="https://salikahmad.vercel.app/" target="_blank">
  <img src="https://img.shields.io/badge/Website-salikahmad.vercel.app-22d3ee?style=for-the-badge&labelColor=020817&color=0e3a6e" />
</a>
&nbsp;
<a href="https://www.linkedin.com/in/salik-ahmad-programmer/" target="_blank">
  <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=020817" />
</a>
&nbsp;
<a href="https://www.kaggle.com/salikahmad702" target="_blank">
  <img src="https://img.shields.io/badge/Kaggle-Notebooks-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white&labelColor=020817" />
</a>
&nbsp;
<a href="https://github.com/SalikAhmad702" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-Profile-ffffff?style=for-the-badge&logo=github&logoColor=black&labelColor=020817" />
</a>

<br/><br/>

<img src="https://img.shields.io/badge/FOCUS-Web%20Development%20%2F%20Flask%20%2F%20Python-22d3ee?style=for-the-badge&labelColor=020817" />
&nbsp;
<img src="https://img.shields.io/badge/COURSE-DAA%20Spring%202026-f97316?style=for-the-badge&labelColor=020817" />
&nbsp;
<img src="https://img.shields.io/badge/STACK-Flask%20%2F%20Python%20%2F%20SQLite-6366f1?style=for-the-badge&labelColor=020817" />

<br/><br/>

<sub>⭐ Star this repo if it helped you with expense tracking and Flask development.</sub>

</div>
