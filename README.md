# iPaaS Portfolio

A hands-on portfolio exploring the core concepts behind Integration Platform as a Service (iPaaS) tools like Zapier, Make, and n8n. Built from scratch in Python to show a real understanding of how these platforms work under the hood, not just how to use one.

## What is iPaaS?

An iPaaS connects different apps and services together so data can flow between them without manual work. Under the hood, most of them boil down to a few repeating patterns:

- **Triggers** — something happens (a webhook fires, or the platform polls an API on a schedule) and starts a workflow.
- **Filters** — only some events should continue (e.g. "only if status is `open`").
- **Transforms** — reshape data from one app's format into another's.
- **Actions** — do something with the result (call another API, write to a log, send a notification).

This repo has three small, self-contained projects that each demonstrate one piece of that puzzle, building up to a mini workflow engine in the third project.

## Projects

| # | Project | Concept demonstrated |
|---|---------|----------------------|
| 1 | [`01-webhook-basics`](./01-webhook-basics) | Receiving webhooks securely: HMAC signature verification, replay protection, event logging |
| 2 | [`02-data-collector`](./02-data-collector) | Pull-based integration: polling a public API on a schedule, deduplicating, and storing results |
| 3 | [`03-mini-connector-engine`](./03-mini-connector-engine) | Putting it together: a trigger → filter → transform → action pipeline driven by a config file, like a tiny Zapier |
| 4 | [`04-dashboard`](./04-dashboard) | Visualizing the Process: a web dashboard that visualizes data and demonstrates the end-to-end workflow in a simple user interface |

Each project folder has its own README with setup steps and an explanation of the concept it covers.

## Tech stack

Python 3, Flask (webhook receivers), SQLite (event storage), PyYAML (workflow config), `requests` (HTTP calls). No paid services or API keys required — everything runs locally.

## Why this exists

I'm learning how integration platforms work by building the pieces myself instead of just using an existing tool. Each project is intentionally small and readable so the concepts are easy to follow.

## Setup

New to Git/GitHub? See [`GETTING_STARTED.md`](./GETTING_STARTED.md) for a full walkthrough of installing Git, creating a GitHub repo, and pushing this project.

## License

MIT — see [`LICENSE`](./LICENSE).
