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


def get_summary_stats(user_id):
    conn = get_db()
    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    count = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    top = conn.execute(
        "SELECT category FROM expenses WHERE user_id = ? "
        "GROUP BY category ORDER BY SUM(amount) DESC, category LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return {
        "total_spent": round(total, 2),
        "transaction_count": count,
        "top_category": top["category"] if top else "—",
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE user_id = ? GROUP BY category ORDER BY total DESC, category",
        (user_id,),
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
