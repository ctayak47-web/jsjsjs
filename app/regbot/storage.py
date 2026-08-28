from __future__ import annotations

import os
import sqlite3
import threading
from typing import Optional

DB_PATH = os.environ.get("REGBOT_DB_PATH", "data/reg_users.db")

_conn: Optional[sqlite3.Connection] = None
_lock = threading.RLock()


def _get_conn() -> sqlite3.Connection:
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
            _conn = sqlite3.connect(
                DB_PATH,
                check_same_thread=False,
                timeout=5,
            )
            _conn.execute("PRAGMA journal_mode=WAL")
            _conn.execute("PRAGMA synchronous=NORMAL")
            _conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registration_date TEXT,
                    calculated_timestamp INTEGER
                )
                """
            )
            _conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    result_text TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    calculated_timestamp INTEGER NOT NULL,
                    username TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            _conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_chat "
                "ON results(chat_id, id DESC)"
            )
            _conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_target "
                "ON results(target_id)"
            )
            _conn.commit()
        return _conn


def register_user(
    user_id: int,
    username: Optional[str] = None,
    reg_date: Optional[str] = None,
    timestamp: Optional[int] = None,
) -> None:
    with _lock:
        con = _get_conn()
        con.execute(
            """
            INSERT INTO users (
                user_id, username, registration_date, calculated_timestamp
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(excluded.username, users.username),
                registration_date = COALESCE(
                    excluded.registration_date,
                    users.registration_date
                ),
                calculated_timestamp = COALESCE(
                    excluded.calculated_timestamp,
                    users.calculated_timestamp
                )
            """,
            (user_id, username, reg_date, timestamp),
        )
        con.commit()


def touch_user(user_id: int, username: Optional[str] = None) -> None:
    register_user(user_id, username)


def save_result(
    chat_id: int,
    target_id: int,
    result_text: str,
    reg_date: str,
    timestamp: int,
    username: Optional[str] = None,
    source: Optional[str] = None,
) -> None:
    with _lock:
        con = _get_conn()
        con.execute(
            """
            INSERT INTO results (
                chat_id,
                target_id,
                result_text,
                registration_date,
                calculated_timestamp,
                username,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                target_id,
                result_text,
                reg_date,
                timestamp,
                username,
                source,
            ),
        )
        con.commit()


def get_latest_result(chat_id: int) -> Optional[dict]:
    with _lock:
        con = _get_conn()
        cur = con.execute(
            """
            SELECT
                target_id,
                result_text,
                registration_date,
                calculated_timestamp,
                username,
                source
            FROM results
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (chat_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "target_id": row[0],
        "result_text": row[1],
        "reg_date": row[2],
        "timestamp": row[3],
        "username": row[4],
        "source": row[5],
    }


def get_stats() -> int:
    with _lock:
        con = _get_conn()
        cur = con.execute("SELECT COUNT(*) FROM users")
        return int(cur.fetchone()[0])


def all_user_ids() -> list[int]:
    with _lock:
        con = _get_conn()
        cur = con.execute("SELECT user_id FROM users")
        return [int(row[0]) for row in cur.fetchall()]
