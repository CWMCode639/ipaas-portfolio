"""
receiver.py

A minimal webhook receiver, built the way real iPaaS platforms (Zapier, Stripe,
GitHub) receive events: every request is signature-verified and checked for
replay, then logged to a small SQLite database so you can inspect what came in.

Run it:
    python3 receiver.py

Then in a second terminal, run sender.py to fire some sample events at it.
"""

import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

# In a real system this would be a secret only you and the sender know,
# stored in an environment variable / secrets manager -- never committed to git.
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "dev-secret-change-me")

# Reject any event whose timestamp is older than this many seconds.
# This is what stops an attacker from capturing a valid request and
# replaying it later.
MAX_TIMESTAMP_SKEW_SECONDS = 300

DB_PATH = Path(__file__).parent / "events.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            received_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def compute_signature(secret: str, timestamp: str, raw_body: bytes) -> str:
    """
    Signs (timestamp + '.' + body) rather than just the body. Including the
    timestamp in what gets signed means an attacker can't reuse a signature
    with a new timestamp -- both have to match what the sender actually sent.
    """
    signed_payload = timestamp.encode() + b"." + raw_body
    return hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()


@app.route("/webhook", methods=["POST"])
def webhook():
    raw_body = request.get_data()  # raw bytes, exactly as sent -- needed for signature checks
    signature = request.headers.get("X-Signature", "")
    timestamp = request.headers.get("X-Timestamp", "")
    event_id = request.headers.get("X-Event-Id", "")

    if not signature or not timestamp or not event_id:
        return jsonify(error="missing required headers (X-Signature, X-Timestamp, X-Event-Id)"), 400

    # 1. Replay protection: is this request too old?
    try:
        sent_at = float(timestamp)
    except ValueError:
        return jsonify(error="invalid X-Timestamp"), 400

    if abs(time.time() - sent_at) > MAX_TIMESTAMP_SKEW_SECONDS:
        return jsonify(error="timestamp outside allowed window, possible replay"), 400

    # 2. Signature verification: was this really sent by someone who knows the secret,
    #    and has the body been tampered with in transit?
    expected_signature = compute_signature(WEBHOOK_SECRET, timestamp, raw_body)
    if not hmac.compare_digest(expected_signature, signature):
        return jsonify(error="invalid signature"), 401

    # 3. Parse the payload now that we trust it.
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return jsonify(error="body is not valid JSON"), 400

    event_type = payload.get("type", "unknown")

    # 4. Idempotency: if we've already processed this event_id, don't double-process it.
    #    Senders sometimes retry on timeout, so receivers need to tolerate duplicates.
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO events (event_id, event_type, payload, received_at) VALUES (?, ?, ?, ?)",
            (event_id, event_type, json.dumps(payload), time.time()),
        )
        conn.commit()
        status = "stored"
    except sqlite3.IntegrityError:
        status = "duplicate_ignored"
    finally:
        conn.close()

    print(f"[receiver] {status}: {event_type} (event_id={event_id})")
    return jsonify(status=status, event_id=event_id), 200


@app.route("/events", methods=["GET"])
def list_events():
    """Inspect what's been received so far -- handy for the demo, not something
    a real webhook receiver would necessarily expose publicly."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT event_id, event_type, payload, received_at FROM events ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    print(f"[receiver] listening on http://127.0.0.1:5000  (secret={'set' if WEBHOOK_SECRET != 'dev-secret-change-me' else 'default dev secret'})")
    app.run(port=5000)
