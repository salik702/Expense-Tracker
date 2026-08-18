import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db, get_user_by_email
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-secret-change-me")

with app.app_context():
    init_db()
    seed_db()


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

    stats = get_summary_stats(user_id)
    stats["total_spent"] = f"₨{stats['total_spent']:,.2f}"
    stats["transaction_count"] = str(stats["transaction_count"])

    transactions = get_recent_transactions(user_id)
    for txn in transactions:
        txn["date"] = datetime.strptime(txn["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        txn["amount"] = f"₨{txn['amount']:,.2f}"
        if txn["description"] is None:
            txn["description"] = ""

    categories = get_category_breakdown(user_id)
    for cat in categories:
        cat["amount"] = f"₨{cat['amount']:,.2f}"

    return render_template(
        "profile.html",
        user=user, stats=stats,
        transactions=transactions, categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
