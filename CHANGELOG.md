# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow SemVer.

## [1.0.0] — 2026-07-24

First stable release.

### Data & coverage
- World feed registry imported from the official MobilityData catalog:
  **1501 feeds in 71 countries**, every one keyless (no provider API key).
- Weekly-refreshed live status page for every feed (HTTP, latency, size)
  and a deep-check funnel (`reachable → ingested → routable`) proving
  end-to-end compatibility, not just URL availability.
- Curated set of 18 hand-verified feeds (PL/DE/US) incl. Szczecin with
  full GTFS-Realtime (vehicles + trip updates + alerts).

### API
- Map geometry (GeoJSON in real route colors), stops, departure boards,
  door-to-door CSA journey planning, live vehicles (poll + **SSE stream**).
- Browse/activate the whole registry over HTTP: `/feeds`, `/countries`,
  `POST /feeds/{id}/ingest` (admin-key-gated, atomic, concurrency-capped),
  `GET /ingests/{id}` job status.
- RFC 7807 `application/problem+json` on every error path incl. 429.
- Prometheus `/metrics`; single-file Python and JS/TS client SDKs.

### Robustness & security
- Atomic ingest (build dir → rename swap), streamed downloads with hard
  size caps, hostile-zip rejection, stop_times row limits.
- Live delays applied inside the routing scan (impossible transfers
  rejected); GTFS-RT outages degrade gracefully with backoff and stale
  frames; per-feed timezones from `agency.txt`.
- Rate limiting, configurable CORS, RAM prewarm at startup.
- 23 end-to-end tests (hostile zips, midnight `24:xx` times, delayed
  transfers, job lifecycle); CI: ruff + bandit + pip-audit + coverage +
  Docker build on Python 3.9 & 3.12.

[1.0.0]: https://github.com/dimaxus3-dev/public-transit-api/releases/tag/v1.0.0
