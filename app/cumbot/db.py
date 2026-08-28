# -*- coding: utf-8 -*-
"""
db.py - База данных для КончаБота (баланс кончи)
"""

import sqlite3
import os
from threading import Lock

DB_PATH = os.environ.get("CUMBOT_DB_PATH", "data/cumbot.db")

_lock = Lock()


def _get_db():
    """Получить подключение к БД"""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init():
    """Инициализировать таблицы БД"""
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cumbot_balance (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()


def get_balance(user_id: int) -> int:
    """Получить баланс кончи пользователя"""
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM cumbot_balance WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0


def add_balance(user_id: int, amount: int) -> int:
    """Добавить кончу пользователю, вернуть новый баланс"""
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        
        current = get_balance(user_id)
        new_balance = max(0, current + amount)
        
        cursor.execute("""
            INSERT OR REPLACE INTO cumbot_balance (user_id, balance, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, new_balance))
        
        conn.commit()
        conn.close()
        
        return new_balance


def set_balance(user_id: int, balance: int) -> int:
    """Установить баланс кончи пользователю"""
    new_balance = max(0, balance)
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cumbot_balance (user_id, balance, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, new_balance))
        
        conn.commit()
        conn.close()
        
        return new_balance


def get_top_users(limit: int = 10) -> list:
    """Получить топ пользователей по балансу"""
    with _lock:
        conn = _get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, balance
            FROM cumbot_balance
            ORDER BY balance DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [(user_id, balance) for user_id, balance in rows]
