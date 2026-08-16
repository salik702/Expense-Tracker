"""Seed a single random Pakistani user into the database."""
import random
import sys

# Make the database package importable when run as a top-level script
sys.path.insert(0, ".")

from database.db import get_db, init_db
from werkzeug.security import generate_password_hash

# Realistic Pakistani first and last names from a range of regions
# (Punjab, Sindh, KPK, Balochistan, Kashmir, urban centers).
PAKISTANI_FIRST_NAMES = [
    "Ahmed", "Muhammad", "Hassan", "Hussain", "Ali", "Hamza", "Bilal",
    "Usman", "Imran", "Faisal", "Saad", "Zain", "Abdullah", "Yusuf",
    "Omar", "Tariq", "Asad", "Fahad", "Junaid", "Salman", "Kashif",
    "Naveed", "Adeel", "Waqas", "Aamir", "Shoaib", "Danish", "Rizwan",
    "Ayesha", "Fatima", "Sana", "Hira", "Maria", "Saima", "Nida",
    "Anum", "Rabia", "Iqra", "Maham", "Kinza", "Mehak", "Zoya",
    "Khadija", "Sumaiya", "Amna", "Bushra", "Farah", "Nimra", "Saba",
]

PAKISTANI_LAST_NAMES = [
    "Khan", "Ahmed", "Sheikh", "Malik", "Siddiqui", "Qureshi", "Butt",
    "Chaudhry", "Raza", "Hussain", "Abbasi", "Syed", "Hashmi", "Farooqi",
    "Iqbal", "Awan", "Javed", "Akhtar", "Aslam", "Anwar", "Bashir",
    "Mahmood", "Niazi", "Rashid", "Saeed", "Saleem", "Shafiq", "Younis",
    "Afridi", "Khattak", "Yusufzai", "Baloch", "Memon", "Soomro", "Bajwa",
    "Dar", "Mir", "Qazi", "Rehman", "Sultan", "Wazir", "Zaidi",
]


def make_email(first: str, last: str) -> str:
    """Build ahmed.khan42@gmail.com style address with a 2-3 digit suffix."""
    digit_count = random.choice([2, 3])
    suffix = "".join(str(random.randint(0, 9)) for _ in range(digit_count))
    return f"{first.lower()}.{last.lower()}{suffix}@gmail.com"


def email_exists(conn, email: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM users WHERE email = ?", (email,)
    ).fetchone()
    return row is not None


def main() -> None:
    # Make sure the schema exists before we try to insert.
    init_db()

    conn = get_db()
    try:
        # Keep regenerating the email until we find one that is not taken.
        while True:
            first = random.choice(PAKISTANI_FIRST_NAMES)
            last = random.choice(PAKISTANI_LAST_NAMES)
            email = make_email(first, last)
            if not email_exists(conn, email):
                break

        password_hash = generate_password_hash("password123")

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (f"{first} {last}", email, password_hash),
        )
        conn.commit()
        user_id = cur.lastrowid

        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        print("Seeded user:")
        print(f"  id:    {row['id']}")
        print(f"  name:  {row['name']}")
        print(f"  email: {row['email']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
