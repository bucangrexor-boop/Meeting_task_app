import sqlite3
import time

DB = "local.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Table for items
    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE,
        name TEXT NOT NULL,
        qty INTEGER NOT NULL DEFAULT 0,
        updated_at INTEGER NOT NULL
    )
    """)
    # Table for sync metadata
    c.execute("""
    CREATE TABLE IF NOT EXISTS sync_meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_item(uuid, name, qty):
    ts = int(time.time())
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO items(uuid, name, qty, updated_at) VALUES (?, ?, ?, ?)",
              (uuid, name, qty, ts))
    conn.commit()
    conn.close()

def list_items():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT uuid, name, qty, updated_at FROM items ORDER BY updated_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
