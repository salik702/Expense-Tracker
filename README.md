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
  <img src="https://img.shields.io/badge/FRAMEWORK-Flask%20%2B%20Jinja2-61DAFB?style=for-the-badge&logo=flask&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/LANGUAGE-Python%203.13-F7DF1E?style=for-the-badge&logo=python&logoColor=black&labelColor=020817" />
  <img src="https://img.shields.io/badge/STATUS-Development-22c55e?style=for-the-badge&logo=github&logoColor=white&labelColor=020817" />
</p>

<!-- Badge Row 2 -->
<p>
  <img src="https://img.shields.io/badge/DATABASE-SQLite-22d3ee?style=for-the-badge&logo=sqlite&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/STYLING-Custom%20CSS%20%2B%20Design%20Tokens-f97316?style=for-the-badge&logo=css3&logoColor=white&labelColor=020817" />
  <img src="https://img.shields.io/badge/THEME-Dark%20%7C%20Light%20Toggle-646CFF?style=for-the-badge&logo=materialsymbols&logoColor=white&labelColor=020817" />
</p>

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> PROJECT.INIT — WHAT IS THIS?`

**Spendly** is a personal expense tracking web application built with **Flask**. It helps you log expenses, spot spending patterns, and stay on budget — without the spreadsheet headache. Users can add expenses with category, amount, date, and description, then visualize their spending through category breakdowns and monthly summaries.

Built with **Flask + Jinja2** for server-side rendering and **Custom CSS** with design tokens for a warm editorial aesthetic. Features automatic dark/light theme detection with manual toggle. Useful for personal finance management and understanding spending habits.

<br/>

<div align="center">

| `MODULE` | `ROLE` | `STATE` |
| :------: | :----- | :-----: |
| 💰 Expense Logger | Add expenses with category, amount, date | `✅ ACTIVE` |
| 📊 Category Breakdown | Visual spending patterns by category | `✅ READY` |
| 📅 Monthly Summaries | Track spending over time periods | `✅ READY` |
| 🎨 Theme Toggle | Dark/Light mode with localStorage | `✅ READY` |
| 🔐 Authentication | User registration and login system | `🟢 COMING SOON` |
| 👤 User Profile | Personal dashboard and settings | `🟢 COMING SOON` |

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> FEATURES.DECK — KEY CAPABILITIES`

<div align="center">

| `FEATURE` | `DESCRIPTION` |
| :-------: | :----------- |
| 📝 Log Expenses | Add any expense in seconds with all details |
| 📂 Category Management | Organize expenses by custom categories |
| 📈 Spending Patterns | See exactly where your money goes |
| 🗓️ Time Filtering | View spending for any date range |
| 🎯 Budget Tracking | Monitor budget usage and remaining amounts |
| 🌓 Theme Support | Automatic dark/light detection + manual toggle |
| 📱 Responsive Design | Works on desktop and mobile devices |

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> STACK.LOAD — TECHNOLOGIES`

<div align="center">

<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/Jinja2-B4418D?style=for-the-badge&logo=jinja&logoColor=white" />
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
<img src="https://img.shields.io/badge/UV-3B82F6?style=for-the-badge&logo=uv&logoColor=white" />

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> PROJECT.STRUCTURE — REPO LAYOUT`

```text
expense-tracker/
├── app.py                         ← Flask application and all routes
├── pyproject.toml                ← Project metadata and dependencies
├── .python-version               ← Python version constraint (3.13)
├── database/
│   ├── __init__.py
│   └── db.py                     ← Database setup, init, and seeding
├── static/
│   ├── css/
│   │   ├── style.css             ← Global styles and design tokens
│   │   └── landing.css           ← Landing page specific styles
│   └── js/
│       └── main.js               ← Theme toggle and shared JavaScript
└── templates/
    ├── base.html                 ← Base template with navbar and footer
    ├── landing.html              ← Marketing landing page
    ├── login.html                ← User login page
    ├── register.html             ← User registration page
    ├── terms.html                ← Terms and Conditions
    └── privacy.html              ← Privacy Policy
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> LOCAL.SETUP — RUN ON YOUR MACHINE`

```bash
# 1. Clone the repo
git clone https://github.com/SalikAhmad702/expense-tracker.git
cd expense-tracker

# 2. Create virtual environment and install dependencies (using uv - recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# 3. Initialize the database
python -c "from database.db import init_db; init_db()"

# 4. Start the development server
python app.py
# Open http://localhost:5001
```

```bash
# Run tests
pytest
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> ROUTES.MAP — AVAILABLE ENDPOINTS`

<div align="center">

| `ROUTE` | `METHOD` | `DESCRIPTION` | `STATUS` |
| :------ | :------: | :------------ | :------: |
| `/` | GET | Landing page | `✅ ACTIVE` |
| `/register` | GET | User registration page | `✅ ACTIVE` |
| `/login` | GET | User login page | `✅ ACTIVE` |
| `/logout` | GET | User logout | `🟢 PLANNED` |
| `/profile` | GET | User profile dashboard | `🟢 PLANNED` |
| `/expenses/add` | GET/POST | Add new expense | `🟢 PLANNED` |
| `/expenses/<int:id>/edit` | GET/POST | Edit existing expense | `🟢 PLANNED` |
| `/expenses/<int:id>/delete` | POST | Delete expense | `🟢 PLANNED` |
| `/expenses` | GET | View all expenses | `🟢 PLANNED` |
| `/terms` | GET | Terms and Conditions | `✅ ACTIVE` |
| `/privacy` | GET | Privacy Policy | `✅ ACTIVE` |

</div>

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> ROADMAP — FUTURE WORK`

- [ ] User authentication system (Flask-Login)
- [ ] Database models for users and expenses
- [ ] CRUD operations for expenses
- [ ] Expense filtering by date range
- [ ] Category-based spending analysis
- [ ] Monthly budget tracking
- [ ] Export data to CSV/Excel
- [ ] Charts and visualizations (Chart.js)
- [ ] Search functionality for expenses
- [ ] Password reset functionality

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> CONTRIBUTION.PROTOCOL`

```bash
# Fork branch commit PR
git checkout -b feature/your-improvement
git add .
git commit -m "feat: describe your change"
git push origin feature/your-improvement
```

Follow the existing code style. Describe what your PR changes and why.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

## `> DESIGN.AESTHETIC — VISUAL IDENTITY`

Spendly uses a **warm editorial aesthetic** with:

| `ELEMENT` | `DETAILS` |
| :-------- | :-------- |
| Color Palette | Deep green accent (#1a472a), warm paper tones (#f7f6f3) |
| Typography | DM Serif Display for headings, DM Sans for body text |
| Theme Support | Automatic dark/light mode detection + manual override |
| Icons | Custom CSS icons with geometric shapes |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%"/>

<div align="center">

<!-- Footer Waving Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:020817,40:0c1a3a,70:0e3a6e,100:020817&height=200&section=footer&text=SALIK%20AHMAD&fontSize=52&fontColor=ffffff&animation=twinkling&fontAlignY=45&desc=CS%20Student%20%E2%80%A2%20Web%20Developer%20%E2%80%A2%20Algorithm%20Enthusiast&descAlignY=68&descSize=16&descColor=67e8f9" width="100%"/>

<br/>

<!-- Footer Typing -->
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=15&duration=3200&pause=1000&color=22D3EE&center=true&vCenter=true&repeat=true&width=860&height=42&lines=Track+every+rupee.+Own+your+finances.;Add+expenses.+See+patterns.+Stay+on+budget.;Built+with+Flask+and+Python+3.13;Visit+salikahmad.vercel.app" alt="Footer Typing" />

<br/><br/>

<!-- Skill Capsule -->
<img src="https://capsule-render.vercel.app/api?type=soft&color=0:020817,100:0e3a6e&height=58&text=Flask%20%20%7C%20%20Python%20%20%7C%20%20SQLite%20%20%7C%20%20Jinja2%20%20%7C%20%20CSS3%20%20%7C%20%20JS&fontSize=16&fontColor=67e8f9&animation=fadeIn" width="80%" />

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

<sub>Star this repo if it helped you with expense tracking and Flask development.</sub>

</div>
