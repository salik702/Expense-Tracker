"""Seed expenses for a specific user with realistic Pakistani descriptions."""

import random
import sys
from datetime import datetime, timedelta

from database.db import get_db, init_db

# Realistic Pakistani categories: (category, min, max, weight, sample descriptions)
CATEGORY_PROFILES = [
    ("Food", 50, 800, 30, [
        "Biryani from student mess", "Karahi chicken dinner", "Naan and chai",
        "Groceries from Imtiaz", "Fruits from sabzi mandi", "Lunch at office canteen",
        "Doodh patti breakfast", "Ice cream from Wall's", "Shawarma roll",
        "Paratha roll", "Karahi nashta", "Cold drink at cafe",
        "Biscuits and snacks", "Lassi in summer", "Chicken tikka plate",
    ]),
    ("Transport", 20, 500, 22, [
        "Uber ride to office", "Careem intercity", "Petrol for bike",
        "Metro bus ticket", "Rickshaw fare", "Daewoo Express ticket",
        "Fare to airport", "Careem Economy ride", "Indrive to home",
        "Petrol refill - Suzuki", "Diesel for car",
    ]),
    ("Bills", 200, 3000, 14, [
        "K-Electric bill", "SSGC gas bill", "PTCL landline bill",
        "Stormfiber internet", "PTCL Charji recharge", "Water tanker",
        "Mobilink postpaid bill", "Zong recharge", "PTCL Flash fiber",
        "Generator diesel",
    ]),
    ("Health", 100, 2000, 8, [
        "D-Watson pharmacy", "Dr consultation at hospital",
        "Panadol and crocin", "Blood test at Chughtai Lab",
        "Dental checkup", "Eye drops from pharmacy",
        "Vitamins and supplements", "Pharmacy - skin cream",
    ]),
    ("Entertainment", 100, 1500, 8, [
        "Cinepax cinema ticket", "Netflix monthly", "Spotify Premium",
        "Birthday dinner treat", "Coffee at Espresso", "Board game cafe",
        "Concert ticket", "Steam game purchase",
    ]),
    ("Shopping", 200, 5000, 10, [
        "Khaadi lawn suit", "J. kurta purchase", "Bata shoes",
        "Outfitters t-shirt", "Grocery hauler bag",
        "Sapphire unstitched", "Mobile cover", "Kitchen utensils",
        "Books from Saeed Book Bank", "Almas perfume",
    ]),
    ("Other", 50, 1000, 8, [
        "Barber haircut", "Tailor stitching charges", "Mobile load",
        "Charity donation", "School fee top-up", "Stationery",
        "Gift wrap and card", "Parking fee", "Eidi for nephew",
        "Birthday cake from bakery",
    ]),
]

# Distribute categories roughly proportionally (weights above)
CATEGORIES = [c[0] for c in CATEGORY_PROFILES]
WEIGHTS = [c[3] for c in CATEGORY_PROFILES]
PROFILES = {c[0]: (c[1], c[2], c[4]) for c in CATEGORY_PROFILES}


def parse_args(argv):
    if len(argv) != 3:
        return None
    try:
        return int(argv[0]), int(argv[1]), int(argv[2])
    except ValueError:
        return None


def main():
    parsed = parse_args(sys.argv[1:])
    if not parsed:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    user_id, count, months = parsed

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        today = datetime.now()
        # Spread across past <months> months (inclusive of current month)
        # Start of earliest month: today - (months-1) months, day=1
        if months <= 0:
            months = 1
        earliest = (today.replace(day=1) - timedelta(days=30 * (months - 1)))
        # Total day range from earliest start to today
        total_days = max((today - earliest).days, 1)

        rows = []
        for _ in range(count):
            category = random.choices(CATEGORIES, weights=WEIGHTS, k=1)[0]
            lo, hi, descriptions = PROFILES[category]
            amount = round(random.uniform(lo, hi), 2)
            description = random.choice(descriptions)
            days_offset = random.randint(0, total_days)
            date = (earliest + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            rows.append((user_id, amount, category, date, description))

        # Single transaction: rollback if any insert fails
        try:
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        # Report
        dates = [r[3] for r in rows]
        print(f"Inserted {len(rows)} expenses for user_id={user_id}.")
        print(f"Date range: {min(dates)} to {max(dates)} (spread across {months} months)")
        print("Sample (first 5):")
        for r in rows[:5]:
            print(f"  {r[3]}  {r[2]:<14}  Rs.{r[1]:>8.2f}  - {r[4]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
