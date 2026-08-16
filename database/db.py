import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cur.lastrowid

    today = datetime.now()
    month = today.strftime("%Y-%m")
    day = today.day

    expenses = [
        (user_id, 24.50, "Food", f"{month}-{max(day - 2, 1):02d}", "Groceries for the week"),
        (user_id, 6.75, "Transport", f"{month}-{max(day - 4, 1):02d}", "Metro card top-up"),
        (user_id, 89.00, "Bills", f"{month}-{max(day - 6, 1):02d}", "Electricity bill"),
        (user_id, 45.30, "Health", f"{month}-{max(day - 8, 1):02d}", "Pharmacy"),
        (user_id, 15.00, "Entertainment", f"{month}-{max(day - 10, 1):02d}", "Movie night"),
        (user_id, 120.00, "Shopping", f"{month}-{max(day - 12, 1):02d}", "New shoes"),
        (user_id, 10.00, "Other", f"{month}-{max(day - 14, 1):02d}", None),
        (user_id, 32.40, "Food", f"{month}-{max(day - 16, 1):02d}", "Dinner out"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user