import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password_hash):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def _date_clause(date_from, date_to):
    clause, params = "", []
    if date_from:
        clause += " AND date >= ?"
        params.append(date_from)
    if date_to:
        clause += " AND date <= ?"
        params.append(date_to)
    return clause, params


def get_expense_summary(user_id, date_from=None, date_to=None):
    clause, extra = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        total, count = conn.execute(
            "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses "
            "WHERE user_id = ?" + clause,
            [user_id, *extra],
        ).fetchone()
        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ?" + clause
            + " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            [user_id, *extra],
        ).fetchone()
        return {
            "total": total,
            "count": count,
            "top_category": top["category"] if top else None,
        }
    finally:
        conn.close()


def get_category_totals(user_id, date_from=None, date_to=None):
    clause, extra = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        return conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ?" + clause
            + " GROUP BY category ORDER BY total DESC",
            [user_id, *extra],
        ).fetchall()
    finally:
        conn.close()


def get_recent_expenses(user_id, limit=10, date_from=None, date_to=None):
    clause, extra = _date_clause(date_from, date_to)
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, amount, category, date, description FROM expenses "
            "WHERE user_id = ?" + clause
            + " ORDER BY date DESC, id DESC LIMIT ?",
            [user_id, *extra, limit],
        ).fetchall()
    finally:
        conn.close()


def get_profile_data(user_id, date_from=None, date_to=None):
    summary = get_expense_summary(user_id, date_from, date_to)
    categories = [
        {
            "category": row["category"],
            "total": row["total"],
            "percent": round(row["total"] / summary["total"] * 100, 1)
            if summary["total"]
            else 0,
        }
        for row in get_category_totals(user_id, date_from, date_to)
    ]
    recent = [
        dict(row)
        for row in get_recent_expenses(user_id, 10, date_from, date_to)
    ]
    return {"summary": summary, "categories": categories, "recent": recent}


def seed_db():
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        today = date.today()

        def day(n):
            return today.replace(day=n).isoformat()

        expenses = [
            (user_id, 12.50, "Food", day(1), "Lunch at cafe"),
            (user_id, 45.00, "Food", day(5), "Weekly groceries"),
            (user_id, 20.00, "Transport", day(8), "Metro card top-up"),
            (user_id, 120.00, "Bills", day(10), "Electricity bill"),
            (user_id, 35.75, "Health", day(14), "Pharmacy"),
            (user_id, 18.00, "Entertainment", day(18), "Movie tickets"),
            (user_id, 60.99, "Shopping", day(22), "New shoes"),
            (user_id, 10.00, "Other", day(26), "Miscellaneous"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
