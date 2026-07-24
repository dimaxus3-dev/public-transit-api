# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.x (latest release) | ✅ |
| older | ❌ |

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's
private reporting: *Security → Report a vulnerability* on this repository
(GitHub private vulnerability reporting is enabled). You'll get an initial
response within 7 days.

## Design notes relevant to security

- The public API surface is read-only. The only mutating endpoint,
  `POST /feeds/{id}/ingest`, is **disabled entirely** until the operator sets
  `ADMIN_KEY`, and then requires `X-API-Key`.
- Ingest treats every archive as hostile: streamed download with a hard size
  cap, unpacked-size and row-count limits, rejection of path-traversal /
  absolute zip entries, atomic build-and-swap so failures can't corrupt
  served data.
- Rate limiting is on by default (`RATE_LIMIT=120` req/min/IP).
- Unhandled errors return a generic RFC 7807 body; details go to server logs
  only.
- The Docker image runs as a non-root user with a read-only root filesystem
  (see `docker-compose.yml` for the full hardening set).
