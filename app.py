import calendar
import math
import os
import re
import secrets
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import CATEGORIES, get_db, init_db, seed_db, get_user_by_email
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
    insert_expense,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

with app.app_context():
    init_db()
    seed_db()


@app.before_request
def ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


# ------------------------------------------------------------------ #
# Profile helpers                                                     #
# ------------------------------------------------------------------ #

def _parse_date(value):
    if not value:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _add_months(d, months):
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def _preset_ranges(today):
    return [
        ("this_month", "This Month", today.replace(day=1), today),
        ("last_3", "Last 3 Months", _add_months(today, -3), today),
        ("last_6", "Last 6 Months", _add_months(today, -6), today),
    ]


def _build_filter_context(today, start_date, end_date):
    ranges = _preset_ranges(today)
    active_preset = "all_time"
    if start_date is not None and end_date is not None:
        active_preset = "custom"
        for key, _, start, end in ranges:
            if start == start_date and end == end_date:
                active_preset = key
                break

    presets = [
        {
            "key": key,
            "label": label,
            "href": url_for("profile", date_from=start, date_to=end),
            "active": active_preset == key,
        }
        for key, label, start, end in ranges
    ]
    presets.append(
        {
            "key": "all_time",
            "label": "All Time",
            "href": url_for("profile"),
            "active": active_preset == "all_time",
        }
    )
    return presets, active_preset


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name:
        return render_template(
            "register.html", error="Please enter your name.", name=name, email=email
        )
    if not email:
        return render_template(
            "register.html",
            error="Please enter your email address.",
            name=name,
            email=email,
        )
    if "@" not in email:
        return render_template(
            "register.html",
            error="That doesn't look like a valid email address.",
            name=name,
            email=email,
        )
    if not password:
        return render_template(
            "register.html",
            error="Please choose a password.",
            name=name,
            email=email,
        )
    if len(password) < 8:
        return render_template(
            "register.html",
            error="Password must be at least 8 characters long.",
            name=name,
            email=email,
        )
    if not confirm_password:
        return render_template(
            "register.html",
            error="Please confirm your password.",
            name=name,
            email=email,
        )
    if password != confirm_password:
        return render_template(
            "register.html",
            error="Passwords do not match.",
            name=name,
            email=email,
        )

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    if existing is not None:
        conn.close()
        return render_template(
            "register.html",
            error="An account with that email already exists. Try signing in.",
            name=name,
            email=email,
        )

    pw_hash = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, pw_hash),
    )
    conn.commit()
    conn.close()

    session["user_id"] = cur.lastrowid
    session["email"] = email
    session["name"] = name
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # Validation
    if not email or not password:
        return render_template(
            "login.html",
            error="Please enter both email and password."
        )

    # Lookup user
    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    # Login successful
    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["name"] = user["name"]
    session["welcome_message"] = f"Welcome back, {user['name']}!"
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    row = get_user_by_id(user_id)
    if row is None:
        return redirect(url_for("logout"))

    name_parts = row["name"].split()
    initials = (
        "".join(part[0] for part in name_parts[:2]).upper()
        if len(name_parts) >= 2
        else row["name"][:2].upper()
    )
    user = {**row, "initials": initials}

    today = date.today()
    start_date = _parse_date(request.args.get("date_from"))
    end_date = _parse_date(request.args.get("date_to"))

    if start_date is None or end_date is None:
        start_date = end_date = None
    elif start_date > end_date:
        flash("Start date must be before end date.")
        start_date = end_date = None

    presets, active_preset = _build_filter_context(today, start_date, end_date)
    date_from = start_date.isoformat() if start_date is not None else None
    date_to = end_date.isoformat() if end_date is not None else None

    stats = get_summary_stats(user_id, date_from=date_from, date_to=date_to)
    stats["total_spent"] = f"₨{stats['total_spent']:,.2f}"
    stats["transaction_count"] = str(stats["transaction_count"])

    transactions = get_recent_transactions(
        user_id, date_from=date_from, date_to=date_to
    )
    for txn in transactions:
        txn["date"] = datetime.strptime(txn["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        txn["amount"] = f"₨{txn['amount']:,.2f}"
        if txn["description"] is None:
            txn["description"] = ""

    categories = get_category_breakdown(user_id, date_from=date_from, date_to=date_to)
    for cat in categories:
        cat["amount"] = f"₨{cat['amount']:,.2f}"

    return render_template(
        "profile.html",
        user=user, stats=stats,
        transactions=transactions, categories=categories,
        presets=presets, active_preset=active_preset,
        date_from=date_from, date_to=date_to,
    )


@app.route("/analytics")
def analytics():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("analytics.html")


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("add_expense.html", categories=CATEGORIES)

    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)

    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date_str = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()
    form_data = {
        "amount": amount,
        "category": category,
        "date": date_str,
        "description": description,
    }

    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        amount_value = None

    if amount_value is None or not math.isfinite(amount_value) or amount_value <= 0:
        error = "Please enter a valid amount greater than 0."
    elif len(description) > 200:
        error = "Description must be 200 characters or fewer."
    elif category not in CATEGORIES:
        error = "Please choose a valid category."
    elif _parse_date(date_str) is None:
        error = "Please enter a valid date."
    else:
        insert_expense(
            session["user_id"], amount_value, category, date_str, description
        )
        flash("Expense added.")
        return redirect(url_for("profile"))

    return render_template(
        "add_expense.html", error=error, categories=CATEGORIES, **form_data
    )


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
