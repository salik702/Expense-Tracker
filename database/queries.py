from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None

    created = row["created_at"].split(" ")[0]
    member_since = datetime.strptime(created, "%Y-%m-%d").strftime("%B %Y")
    return {"name": row["name"], "email": row["email"], "member_since": member_since}


def _date_where(user_id, date_from, date_to):
    where = "WHERE user_id = ?"
    params = [user_id]
    if date_from and date_to:
        where += " AND date BETWEEN ? AND ?"
        params += [date_from, date_to]
    return where, tuple(params)


def get_summary_stats(user_id, date_from=None, date_to=None):
    where, params = _date_where(user_id, date_from, date_to)
    conn = get_db()
    total = conn.execute(
        f"SELECT COALESCE(SUM(amount), 0) FROM expenses {where}", params
    ).fetchone()[0]
    count = conn.execute(
        f"SELECT COUNT(*) FROM expenses {where}", params
    ).fetchone()[0]
    top = conn.execute(
        f"SELECT category FROM expenses {where} "
        "GROUP BY category ORDER BY SUM(amount) DESC, category LIMIT 1",
        params,
    ).fetchone()
    conn.close()
    return {
        "total_spent": round(total, 2),
        "transaction_count": count,
        "top_category": top["category"] if top else "—",
    }


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    where, params = _date_where(user_id, date_from, date_to)
    conn = get_db()
    rows = conn.execute(
        f"SELECT id, date, description, category, amount FROM expenses {where} "
        "ORDER BY date DESC, id DESC LIMIT ?",
        params + (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


def get_expense(id):
    conn = get_db()
    row = conn.execute(
        "SELECT id, user_id, amount, category, date, description FROM expenses "
        "WHERE id = ?",
        (id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def update_expense(id, amount, category, date, description):
    conn = get_db()
    try:
        conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? "
            "WHERE id = ?",
            (amount, category, date, description or None, id),
        )
        conn.commit()
    finally:
        conn.close()


def get_category_breakdown(user_id, date_from=None, date_to=None):
    where, params = _date_where(user_id, date_from, date_to)
    conn = get_db()
    rows = conn.execute(
        f"SELECT category, SUM(amount) AS total FROM expenses {where} "
        "GROUP BY category ORDER BY total DESC, category",
        params,
    ).fetchall()
    conn.close()
    if not rows:
        return []

    total = sum(row["total"] for row in rows)
    breakdown = []
    for row in rows:
        breakdown.append(
            {
                "name": row["category"],
                "amount": round(row["total"], 2),
                "pct": round(row["total"] / total * 100),
            }
        )

    remainder = 100 - sum(item["pct"] for item in breakdown)
    if remainder:
        breakdown[0]["pct"] += remainder
    return breakdown


def insert_expense(user_id, amount, category, date, description):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description or None),
        )
        conn.commit()
    finally:
        conn.close()
