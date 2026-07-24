"""
sender.py

Plays the role of an external service (like GitHub or Stripe) firing webhook
events at receiver.py. Signs each request the same way a real provider would,
so receiver.py can verify it's genuine.

Run receiver.py first, then in a second terminal:
    python3 sender.py                  # sends 3 sample events, one duplicate, one tampered (all logged)
    python3 sender.py --count 10       # send 10 events
"""

import argparse
import hashlib
import hmac
import json
import os
import time
import uuid

import requests

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "dev-secret-change-me")
RECEIVER_URL = os.environ.get("RECEIVER_URL", "http://127.0.0.1:5000/webhook")

SAMPLE_EVENT_TYPES = ["user.created", "order.paid", "ticket.updated"]


def sign(secret: str, timestamp: str, raw_body: bytes) -> str:
    signed_payload = timestamp.encode() + b"." + raw_body
    return hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()


def send_event(event_type: str, data: dict, event_id: str = None, bad_signature: bool = False):
    event_id = event_id or str(uuid.uuid4())
    payload = {"type": event_type, "data": data}
    raw_body = json.dumps(payload).encode()
    timestamp = str(time.time())

    signature = sign(WEBHOOK_SECRET, timestamp, raw_body)
    if bad_signature:
        signature = "0" * 64  # simulate a forged/corrupted request

    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "X-Event-Id": event_id,
    }

    resp = requests.post(RECEIVER_URL, data=raw_body, headers=headers, timeout=5)
    print(f"[sender] sent {event_type} (event_id={event_id}) -> {resp.status_code} {resp.json()}")
    return event_id


def main():
    parser = argparse.ArgumentParser(description="Fire sample webhook events at receiver.py")
    parser.add_argument("--count", type=int, default=3, help="number of normal events to send")
    args = parser.parse_args()

    sent_ids = []
    for i in range(args.count):
        event_type = SAMPLE_EVENT_TYPES[i % len(SAMPLE_EVENT_TYPES)]
        event_id = send_event(event_type, {"index": i, "note": "sample payload"})
        sent_ids.append(event_id)
        time.sleep(0.3)

    # Demonstrate idempotency: resend the first event with the same event_id.
    if sent_ids:
        print("[sender] resending the first event to demonstrate duplicate handling...")
        send_event(SAMPLE_EVENT_TYPES[0], {"index": 0, "note": "resent"}, event_id=sent_ids[0])

    # Demonstrate signature verification: send one with a deliberately wrong signature.
    print("[sender] sending a tampered/forged request to demonstrate signature rejection...")
    send_event("user.created", {"index": -1, "note": "should be rejected"}, bad_signature=True)


if __name__ == "__main__":
    main()
