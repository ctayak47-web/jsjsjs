import sqlite3
import os

DB_PATH = os.environ.get("ECONOMY_DB_PATH", "data/economy.db")

_conn = None


def _get_conn():
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return _conn


def init():
    con = _get_conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 5000,
            last_bonus TEXT DEFAULT '0',
            is_admin INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_games (
            user_id INTEGER PRIMARY KEY,
            game_type TEXT,
            bet INTEGER,
            state TEXT,
            step INTEGER,
            message_id INTEGER
        )
    """)
    con.commit()


def get_user(user_id, username=None):
    if not username:
        username = "Игрок"
    con = _get_conn()
    cur = con.cursor()
    cur.execute("SELECT username, balance, last_bonus, is_admin FROM users WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    if not res:
        cur.execute(
            "INSERT INTO users (user_id, username, balance, last_bonus, is_admin) VALUES (?, ?, 5000, '0', 0)",
            (user_id, username),
        )
        con.commit()
        return username, 5000, "0", 0
    return res


def update_balance(user_id, amount):
    con = _get_conn()
    con.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    con.commit()


def check_admin(user_id):
    con = _get_conn()
    cur = con.cursor()
    cur.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    return bool(res and res[0] == 1)


def make_admin(user_id):
    con = _get_conn()
    con.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    con.commit()


def find_user_by_username(username):
    clean_username = username.replace("@", "").strip()
    con = _get_conn()
    cur = con.cursor()
    cur.execute("SELECT user_id, username FROM users WHERE LOWER(username) = LOWER(?)", (clean_username,))
    return cur.fetchone()


def set_last_bonus(user_id, ts):
    con = _get_conn()
    con.execute("UPDATE users SET last_bonus = ? WHERE user_id = ?", (str(ts), user_id))
    con.commit()


# ─── active games ────────────────────────────────────────────────────────────

def get_active_game(user_id, game_type=None):
    con = _get_conn()
    cur = con.cursor()
    if game_type:
        cur.execute("SELECT bet, state, step FROM active_games WHERE user_id = ? AND game_type = ?", (user_id, game_type))
    else:
        cur.execute("SELECT game_type FROM active_games WHERE user_id = ?", (user_id,))
    return cur.fetchone()


def create_game(user_id, game_type, bet, state, message_id=0):
    con = _get_conn()
    con.execute(
        "INSERT INTO active_games (user_id, game_type, bet, state, step, message_id) VALUES (?, ?, ?, ?, 0, ?)",
        (user_id, game_type, bet, state, message_id),
    )
    con.commit()


def update_game(user_id, **kwargs):
    if not kwargs:
        return
    con = _get_conn()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    con.execute(f"UPDATE active_games SET {sets} WHERE user_id=?", vals)
    con.commit()


def delete_game(user_id):
    con = _get_conn()
    con.execute("DELETE FROM active_games WHERE user_id = ?", (user_id,))
    con.commit()


def all_user_ids():
    con = _get_conn()
    cur = con.cursor()
    cur.execute("SELECT user_id FROM users")
    return [row[0] for row in cur.fetchall()]
