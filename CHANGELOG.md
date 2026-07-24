# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow SemVer.

## [1.0.1] — 2026-07-24

### Added
- **Prebuilt single-file binaries** for Linux x64, Windows x64, macOS Intel
  and macOS Apple Silicon on every release — download, `chmod +x`, run; the
  feed registry (1500+ cities) is embedded, no Python required.
- `python -m app` entry point with `--host/--port` flags.
- `TRANSIT_DATA_DIR` environment variable to relocate ingested data.
- Combined `SHA256SUMS` covering binaries, source archive and SBOM.
- Docker image now also tagged `vX.Y.Z` (in addition to `X.Y.Z`, `X.Y`,
  `latest`).
- README badges: latest release, downloads, GHCR image, coverage.

### Changed
- Every release's binaries are smoke-tested (server boots, `/health`
  answers) on all four platforms before publishing.
- Full-registry deep check: all **1501 feeds** now verified end-to-end
  (1436 reachable → 1387 ingested → 751 routable), replacing the
  120-feed sample.

### Fixed
- Data paths are now frozen-binary-aware (bundled registry files resolve
  from the executable; writable data defaults to `./data`).

## [1.0.0] — 2026-07-24

First stable release.

### Added
- World feed registry from the official MobilityData catalog: **1501
  keyless feeds in 71 countries**; browse via `/feeds`, `/countries`,
  activate over HTTP (`POST /feeds/{id}/ingest`, admin-gated, atomic,
  concurrency-capped) with `GET /ingests/{id}` job status.
- Map geometry (GeoJSON in real route colors), stops, departure boards,
  door-to-door CSA journey planning, live vehicles (poll + SSE stream).
- Weekly-refreshed live status page for every feed and a deep-check
  funnel (`reachable → ingested → routable`).
- RFC 7807 `application/problem+json` on every error path; Prometheus
  `/metrics`; single-file Python and JS/TS client SDKs.
- Quality gates: ruff, bandit, pip-audit, coverage floor, Docker
  smoke-run, CodeQL, Dependabot; hardened non-root Docker image; GHCR
  publishing with SPDX SBOM and checksums.

### Changed
- Live GTFS-RT delays are applied inside the routing scan, so impossible
  transfers are rejected and faster live alternatives win.
- Per-feed timezones come from `agency.txt` captured at ingest.

### Fixed
- Late-night departure boards crashed on a SQL binding bug (shadowed
  variable); `/journey` returned HTTP 500 for feeds with expired
  calendars; leg timestamps double-counted realtime delays.

[1.0.1]: https://github.com/dimaxus3-dev/public-transit-api/releases/tag/v1.0.1
[1.0.0]: https://github.com/dimaxus3-dev/public-transit-api/releases/tag/v1.0.0
