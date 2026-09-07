import sqlite3
from pathlib import Path

DB=Path(__file__).resolve().parent/"app.db"

def conn():
    c=sqlite3.connect(DB,check_same_thread=False)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    c=conn()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(
        telegram_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        first_name TEXT DEFAULT 'Player',
        stars INTEGER DEFAULT 0,
        bonus_claimed INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS nft_catalog(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        rarity TEXT NOT NULL,
        price INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS inventory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        nft_id INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS upgrades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        target_nft_id INTEGER NOT NULL,
        chance REAL NOT NULL,
        won INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    if c.execute("SELECT COUNT(*) FROM nft_catalog").fetchone()[0]==0:
        rows=[
        (1,"Pixel Bunny","◈","COMMON",120),(2,"Neon Cat","✦","COMMON",160),
        (3,"Cyber Fox","◉","RARE",250),(4,"Void Wolf","◆","RARE",360),
        (5,"Solar Tiger","✹","EPIC",560),(6,"Phantom Crow","✧","EPIC",820),
        (7,"Golden Serpent","◊","LEGENDARY",1400),(8,"Cosmic Crown","✺","LEGENDARY",2400),
        (9,"Virus Core","⬡","MYTHIC",4500),(10,"Black Hole","◉","MYTHIC",8000)]
        c.executemany("INSERT INTO nft_catalog VALUES(?,?,?,?,?)",rows)
    c.commit();c.close()

def ensure_user(tid,username="",first_name="Player"):
    c=conn()
    c.execute("INSERT OR IGNORE INTO users(telegram_id,username,first_name) VALUES(?,?,?)",(tid,username,first_name))
    if username or first_name:
        c.execute("UPDATE users SET username=?,first_name=? WHERE telegram_id=?",(username,first_name,tid))
    c.commit()
    n=c.execute("SELECT COUNT(*) FROM inventory WHERE telegram_id=?",(tid,)).fetchone()[0]
    if n==0:
        c.executemany("INSERT INTO inventory(telegram_id,nft_id) VALUES(?,?)",[(tid,1),(tid,2),(tid,3)])
        c.commit()
    c.close()

def get_profile(tid):
    ensure_user(tid)
    c=conn()
    user=dict(c.execute("SELECT * FROM users WHERE telegram_id=?",(tid,)).fetchone())
    inv=[dict(x) for x in c.execute('''
    SELECT inventory.id inventory_id,nft_catalog.* FROM inventory
    JOIN nft_catalog ON nft_catalog.id=inventory.nft_id
    WHERE inventory.telegram_id=? ORDER BY nft_catalog.price
    ''',(tid,)).fetchall()]
    c.close()
    return user,inv
