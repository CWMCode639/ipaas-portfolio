"""
storage.py

Small SQLite helper for the collector. Kept separate from collector.py so the
"where do I put the data" concern is isolated from the "how do I fetch it"
concern -- a pattern real integration platforms use heavily.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "collected.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS collected_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_event_id TEXT UNIQUE NOT NULL,
            event_type TEXT,
            actor TEXT,
            repo TEXT,
            created_at TEXT,
            collected_at REAL NOT NULL,
            raw_json TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_event(source_event_id: str, event_type: str, actor: str, repo: str, created_at: str,
               raw_json: str, collected_at: float) -> bool:
    """Returns True if this was a new event, False if it was already collected."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO collected_events
                (source_event_id, event_type, actor, repo, created_at, collected_at, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (source_event_id, event_type, actor, repo, created_at, collected_at, raw_json),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def count_events() -> int:
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM collected_events").fetchone()[0]
    conn.close()
    return n
