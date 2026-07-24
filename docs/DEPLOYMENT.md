# Deployment

## Quick self-host (Docker, recommended)

```bash
docker compose up --build        # → http://localhost:8000/docs
```

The compose file ships hardened defaults: non-root user, read-only root
filesystem, `no-new-privileges`, all capabilities dropped, tmpfs `/tmp`,
CPU/RAM limits, an init process and a healthcheck. Feed artifacts persist in
the `transit-data` volume.

Pre-load cities at build time or via a one-off command:

```bash
docker compose run --rm api python -m app.ingest mdb-648   # Vienna
```

## Bare metal / VM

```bash
pip install -r requirements.txt
python -m app.ingest szczecin-zditm
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run **one Uvicorn worker per instance** (state is per-process; see
ARCHITECTURE.md). Scale horizontally behind any load balancer — instances
warm their caches independently and need no coordination.

## Configuration (environment)

| Variable | Default | Meaning |
|---|---|---|
| `RATE_LIMIT` | `120` | Requests/min per client IP; `0` disables |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `ADMIN_KEY` | unset | Enables + protects `POST /feeds/{id}/ingest` |
| `PREWARM` | `1` | Pre-build routing graphs in RAM at startup |
| `INGEST_MAX_ZIP_MB` | `250` | Download size cap |
| `INGEST_MAX_UNPACKED_MB` | `2500` | Unpacked archive cap |
| `INGEST_MAX_STOP_TIMES` | `8000000` | stop_times row cap |

## Production checklist

- [ ] Set `ADMIN_KEY` (or leave HTTP ingest disabled and ingest via CLI/cron).
- [ ] Restrict `CORS_ORIGINS` to your frontend origin(s).
- [ ] Point Prometheus at `/metrics`; alert on `transit_requests_total`
      5xx growth and on `/health` failures.
- [ ] Schedule feed refreshes (idempotent):
      `0 4 * * * python -m app.ingest <id>` per city, or re-run
      `scripts/import_catalog.py` weekly for the registry itself.
- [ ] Put a CDN/HTTP cache in front of `/map/*` and `/routes/*` — responses
      are immutable between ingests.
- [ ] Snapshot the `transit-data` volume if you need instant rollback.
