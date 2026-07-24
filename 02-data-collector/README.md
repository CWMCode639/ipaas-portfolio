# 02 — Data Collector (polling)

Webhooks are a "push" integration: the source notifies you. Not every API
supports that, so integration platforms also need a "pull" mode: check the
source on a schedule and collect anything new. This project polls GitHub's
public events API for a repo of your choice.

Concepts demonstrated:

- **Polling on an interval** instead of waiting for a push.
- **Deduplication** — events are keyed by their unique ID in SQLite, so
  polling the same window twice doesn't create duplicate rows.
- **Being a polite API consumer** — uses ETags so unchanged responses don't
  count against the rate limit (a `304 Not Modified` costs nothing).

## Run it

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 collector.py --repo python/cpython --once
```

Drop `--once` to poll continuously:

```
python3 collector.py --repo python/cpython --interval 60
```

Try it on a repo with more activity to see more events, e.g. `--repo torvalds/linux`.

## Inspect what was collected

```
python3 -c "import sqlite3; c = sqlite3.connect('collected.db'); [print(r) for r in c.execute('SELECT event_type, actor, repo, created_at FROM collected_events ORDER BY id DESC LIMIT 10')]"
```

## Files

- `collector.py` — fetches events from GitHub's public API and hands new ones to `storage.py`.
- `storage.py` — SQLite persistence layer (`collected.db`, created on first run).
