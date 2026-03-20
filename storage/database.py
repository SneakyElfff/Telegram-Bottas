import json
import logging
import sqlite3
from typing import List, Dict, Any
from config.config import DATA_DIR

logger = logging.getLogger(__name__)

DB_PATH = DATA_DIR / 'F1_press_schedule_bot.db'
_conn: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
        _conn.execute("PRAGMA journal_mode = WAL")
        _conn.execute("PRAGMA busy_timeout = 5000")
        _conn.row_factory = sqlite3.Row
    return _conn

def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            chat_id INTEGER PRIMARY KEY,
            subscribed_at TEXT DEFAULT (datetime('now')),
            active BOOLEAN DEFAULT 1
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    conn.commit()
    logger.info("Database initialized at %s", DB_PATH)

# ────────────────────────────────────────────────
# Subscribers
# ────────────────────────────────────────────────

def get_subscribers(active_only: bool = True) -> List[int]:
    conn = get_connection()

    query = "SELECT chat_id FROM subscribers"
    if active_only:
        query += " WHERE active = 1"

    rows = conn.execute(query).fetchall()
    return [row["chat_id"] for row in rows]

def add_subscriber(chat_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)",
            (chat_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as error:
        logger.error("Failed to add a subscriber: %s", error)
        return False

def remove_subscriber(chat_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE subscribers SET active = 0 WHERE chat_id = ?",
            (chat_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as error:
        logger.error("Failed to remove the subscriber: %s", error)
        return False

# ────────────────────────────────────────────────
# Persistent state (last_notified)
# ────────────────────────────────────────────────

def load_last_notified() -> Dict[str, Any]:
    default: Dict[str, Any] = {"round": 0, "year": 2026}
    conn = get_connection()
    row = conn.execute("SELECT value FROM state WHERE key = 'last_notified'"
                       ).fetchone()
    if row:
        return json.loads(row["value"])

    save_last_notified(default)

    return default

def save_last_notified(data: Dict[str, Any]):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO state (key, value) VALUES ('last_notified', ?)",
        (json.dumps(data, separators=(",", ":")),),
    )
    conn.commit()