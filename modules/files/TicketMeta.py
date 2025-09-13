import json
import os
import sqlite3
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "tickets.db")
LEGACY_JSON_PATH = os.path.join(DATA_DIR, "tickets.json")


def _ensure_db() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id TEXT PRIMARY KEY,
                meta TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _migrate_from_legacy_json() -> None:
    if not os.path.exists(LEGACY_JSON_PATH):
        return
    try:
        with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return
    except Exception:
        return

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM tickets")
        count = cur.fetchone()[0]
        if count:
            return
        for channel_id, meta in data.items():
            cur.execute(
                "INSERT OR REPLACE INTO tickets (channel_id, meta) VALUES (?, ?)",
                (str(channel_id), json.dumps(meta, ensure_ascii=False)),
            )
        conn.commit()


def _get(conn: sqlite3.Connection, channel_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT meta FROM tickets WHERE channel_id = ?", (str(channel_id),))
    row = cur.fetchone()
    if not row:
        return None
    try:
        return json.loads(row[0]) if row[0] else None
    except Exception:
        return None


def set_ticket(channel_id: int, meta: Dict[str, Any]) -> None:
    _ensure_db()
    _migrate_from_legacy_json()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO tickets (channel_id, meta) VALUES (?, ?)",
            (str(channel_id), json.dumps(meta, ensure_ascii=False)),
        )
        conn.commit()


def get_ticket(channel_id: int) -> Optional[Dict[str, Any]]:
    _ensure_db()
    _migrate_from_legacy_json()
    with sqlite3.connect(DB_PATH) as conn:
        return _get(conn, channel_id)


def update_ticket(channel_id: int, updates: Dict[str, Any]) -> None:
    _ensure_db()
    _migrate_from_legacy_json()
    with sqlite3.connect(DB_PATH) as conn:
        current = _get(conn, channel_id) or {}
        current.update(updates)
        conn.execute(
            "INSERT OR REPLACE INTO tickets (channel_id, meta) VALUES (?, ?)",
            (str(channel_id), json.dumps(current, ensure_ascii=False)),
        )
        conn.commit()


def delete_ticket(channel_id: int) -> None:
    _ensure_db()
    _migrate_from_legacy_json()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM tickets WHERE channel_id = ?", (str(channel_id),))
        conn.commit()


