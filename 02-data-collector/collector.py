"""
collector.py

The "pull" counterpart to webhooks: instead of waiting for someone to notify
you, you poll a source on a schedule and collect anything new. This is how
iPaaS platforms integrate with APIs that don't support webhooks.

Source used here: GitHub's public events API (no auth needed for low volume).
https://api.github.com/repos/{owner}/{repo}/events

Run it:
    python3 collector.py --repo python/cpython --once      # collect one batch and exit
    python3 collector.py --repo python/cpython --interval 60   # poll every 60s forever
"""

import argparse
import time

import requests

import storage

USER_AGENT = "ipaas-portfolio-data-collector (educational project)"


def fetch_events(repo: str, etag: str = None):
    """
    Fetch recent public events for a repo. Uses an ETag if we have one from a
    previous request -- GitHub returns 304 Not Modified (and doesn't count it
    against the rate limit) if nothing changed since then. This is the same
    "be polite to the API" pattern real connectors use.
    """
    url = f"https://api.github.com/repos/{repo}/events"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if etag:
        headers["If-None-Match"] = etag

    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code == 304:
        return [], etag  # nothing new
    resp.raise_for_status()
    return resp.json(), resp.headers.get("ETag")


def collect_once(repo: str, etag: str = None):
    events, new_etag = fetch_events(repo, etag)

    new_count = 0
    for event in events:
        inserted = storage.save_event(
            source_event_id=event["id"],
            event_type=event.get("type"),
            actor=(event.get("actor") or {}).get("login"),
            repo=(event.get("repo") or {}).get("name"),
            created_at=event.get("created_at"),
            raw_json=str(event),
            collected_at=time.time(),
        )
        if inserted:
            new_count += 1

    print(f"[collector] fetched {len(events)} event(s), {new_count} new, "
          f"total stored: {storage.count_events()}")
    return new_etag


def main():
    parser = argparse.ArgumentParser(description="Poll GitHub public events for a repo")
    parser.add_argument("--repo", default="python/cpython", help="owner/repo to watch")
    parser.add_argument("--interval", type=int, default=60, help="seconds between polls")
    parser.add_argument("--once", action="store_true", help="collect a single batch and exit")
    args = parser.parse_args()

    storage.init_db()

    etag = None
    print(f"[collector] watching {args.repo}")
    if args.once:
        collect_once(args.repo, etag)
        return

    while True:
        etag = collect_once(args.repo, etag)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
