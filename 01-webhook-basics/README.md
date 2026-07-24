# 01 — Webhook Basics

A webhook is just an HTTP POST request that one service sends to another when
something happens (e.g. "a new order was paid"). This project shows the parts
that make receiving webhooks *safe*, which is the part most tutorials skip:

- **Signature verification** — every request is signed with HMAC-SHA256 using
  a shared secret. The receiver recomputes the signature and rejects the
  request if it doesn't match, so a forged request gets rejected.
- **Replay protection** — each request includes a timestamp, and the receiver
  rejects anything older than 5 minutes, so a captured request can't be
  resent later.
- **Idempotency** — each event has a unique `event_id`. If the same event
  arrives twice (senders retry on timeout), the receiver only processes it
  once.

## Run it

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 receiver.py
```

In a second terminal (same venv activated):

```
python3 sender.py
```

You'll see the sender fire 3 sample events, resend one to show duplicate
handling, then send a forged one to show it getting rejected with a 401.

Check what the receiver logged:

```
curl http://127.0.0.1:5000/events
```

## Files

- `receiver.py` — Flask app that verifies and stores incoming events in `events.db` (SQLite, created on first run).
- `sender.py` — simulates an external service sending signed webhook events.

## Configuration

Both scripts read `WEBHOOK_SECRET` from the environment (defaults to a
placeholder dev secret). To use a custom one:

```
export WEBHOOK_SECRET="something-only-you-know"
```
