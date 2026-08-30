import sqlite3
import os
import time
from threading import Lock

DB_PATH = os.environ.get("CUMBOT_DB_PATH", "data/cumbot.db")

_lock = Lock()


def _get_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init():
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cumbot_balance (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # миграция для баз, созданных до появления колонки username
        cursor.execute("PRAGMA table_info(cumbot_balance)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        if "username" not in existing_columns:
            cursor.execute("ALTER TABLE cumbot_balance ADD COLUMN username TEXT")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cumbot_cooldown (
                user_id INTEGER PRIMARY KEY,
                last_fire REAL NOT NULL DEFAULT 0
            )
            """
        )

        conn.commit()
        conn.close()


def get_balance(user_id: int) -> int:
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM cumbot_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0


def add_balance(user_id: int, amount: int, username: str = None) -> int:
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM cumbot_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        current = row[0] if row else 0
        new_balance = max(0, current + amount)

        cursor.execute(
            """
            INSERT INTO cumbot_balance (user_id, username, balance) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                balance = excluded.balance,
                username = COALESCE(excluded.username, cumbot_balance.username)
            """,
            (user_id, username, new_balance),
        )
        conn.commit()
        conn.close()

        return new_balance


def set_balance(user_id: int, balance: int, username: str = None) -> int:
    new_balance = max(0, balance)
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cumbot_balance (user_id, username, balance) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                balance = excluded.balance,
                username = COALESCE(excluded.username, cumbot_balance.username)
            """,
            (user_id, username, new_balance),
        )
        conn.commit()
        conn.close()

        return new_balance


def get_top_users(limit: int = 10) -> list:
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, balance FROM cumbot_balance ORDER BY balance DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [(user_id, username, balance) for user_id, username, balance in rows]


def get_last_fire(user_id: int) -> float:
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT last_fire FROM cumbot_cooldown WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0


def set_last_fire(user_id: int, timestamp: float = None) -> float:
    if timestamp is None:
        timestamp = time.time()
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cumbot_cooldown (user_id, last_fire) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_fire = excluded.last_fire
            """,
            (user_id, timestamp),
        )
        conn.commit()
        conn.close()
        return timestamp