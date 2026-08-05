import sqlite3
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Open a connection to the SQLite database with row access by column
    name and foreign key enforcement enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert one demo user and 8 sample expenses, but only if the users
    table is empty. Safe to call on every startup."""
    conn = get_db()

    existing = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    if existing is not None:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    first_of_month = today.replace(day=1)

    sample_expenses = [
        (12.50, "Food", 1, "Groceries"),
        (35.00, "Transport", 3, "Monthly bus pass"),
        (85.00, "Bills", 5, "Electricity bill"),
        (20.00, "Health", 7, "Pharmacy"),
        (45.99, "Entertainment", 10, "Movie night"),
        (60.00, "Shopping", 13, "New shoes"),
        (15.00, "Other", 15, "Miscellaneous"),
        (28.75, "Food", 18, "Restaurant dinner"),
    ]

    for amount, category, day_offset, description in sample_expenses:
        expense_date = first_of_month + timedelta(days=day_offset - 1)
        if expense_date.month != first_of_month.month:
            expense_date = today
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, expense_date.isoformat(), description),
        )

    conn.commit()
    conn.close()
