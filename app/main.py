"""
City-transit read API — map geometry, stops, live vehicles and A→B routing.

Turns official GTFS Static feeds into per-city GeoJSON line layers (real route
colors) and stop lists, plans door-to-door city journeys (walk + rides +
transfers) with a stdlib Connection Scan router, and overlays live
positions/delays where a feed publishes GTFS-Realtime. No API keys, no
database — artifacts are flat files.

    pip install -r requirements.txt
    python -m app.ingest szczecin-zditm      # download + build artifacts
    uvicorn app.main:app --reload

Optional hardening (all via environment variables, all off by default):
    CORS_ORIGINS   comma-separated allowed origins (default "*")
    RATE_LIMIT     requests per minute per client IP (default 120; 0 = off)
    ADMIN_KEY      when set, POST /feeds/{id}/ingest requires X-API-Key
"""
import datetime as dt
import json
import os
import threading
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

from . import ingest as ingest_mod
from . import realtime, registry, routing, schedule, store

from contextlib import asynccontextmanager


@asynccontextmanager
async def _lifespan(_app):
    _start_prewarm()      # defined below; lifts ingested cities into RAM
    yield


app = FastAPI(
    lifespan=_lifespan,
    title="City Transit API",
    version="1.2.0",
    description=(
        "Keyless GTFS backend for city public transport: map-ready route "
        "geometry, stops, departure boards, door-to-door journey planning and "
        "live vehicle positions (GTFS-Realtime), for 1500+ feeds in 70+ "
        "countries.\n\n"
        "- Interactive docs: this page (`/docs`) · machine-readable schema: `/openapi.json`\n"
        "- Errors follow **RFC 7807** (`application/problem+json`)\n"
        "- Prometheus metrics at `/metrics`\n"
        "- Live vehicles as **SSE** at `/vehicles/stream`"
    ),
    license_info={"name": "PolyForm Noncommercial 1.0.0",
                  "url": "https://polyformproject.org/licenses/noncommercial/1.0.0/"},
)

_FEEDS = registry.load()

# ── CORS (env-configurable; "*" by default so the API is easy to try) ────────
_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=_origins,
                   allow_methods=["GET", "POST"], allow_headers=["X-API-Key"])

# ── Rate limiting (sliding window per client IP, in-memory) ──────────────────
_RATE = int(os.environ.get("RATE_LIMIT", "120"))          # req/min; 0 disables
_hits: dict = defaultdict(deque)
_hits_lock = threading.Lock()


@app.middleware("http")
async def _rate_limit(request: Request, call_next):
    if _RATE > 0:
        ip = request.client.host if request.client else "?"
        now = time.time()
        with _hits_lock:
            q = _hits[ip]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= _RATE:
                # Same RFC 7807 problem+json contract as every other error.
                return _problem(429, f"rate limit exceeded ({_RATE} requests/min)",
                                str(request.url.path))
            q.append(now)
    return await call_next(request)


_ADMIN_KEY = os.environ.get("ADMIN_KEY", "")
_ingesting: set = set()


# ── Startup pre-warm: lift every ingested city's graph into RAM ──────────────
# Routing/geometry caches are lazy (first request pays the build cost). On
# startup a daemon thread walks the ingested feeds and pre-builds today's
# routing graph + geometry, so the first user is as fast as the thousandth.
# Disable with PREWARM=0 (e.g. in tests or memory-tight environments).

def _prewarm_feeds() -> int:
    warmed = 0
    today = dt.datetime.now().strftime("%Y%m%d")
    for fid in store.available_feeds():
        try:
            store.routes(fid)
            store.center(fid)
            routing._stops(fid)
            routing._footpaths(fid)
            routing._day_connections(fid, today)
            warmed += 1
        except Exception:  # noqa: BLE001 — a bad feed must not break startup
            pass
    return warmed


def _start_prewarm():
    if os.environ.get("PREWARM", "1") != "0":
        threading.Thread(target=_prewarm_feeds, daemon=True).start()

# ── RFC 7807 problem+json error responses ────────────────────────────────────
_STATUS_TITLES = {400: "Bad Request", 401: "Unauthorized", 404: "Not Found",
                  422: "Validation Error", 429: "Too Many Requests",
                  500: "Internal Server Error", 502: "Bad Gateway"}


def _problem(status: int, detail, instance: str = ""):
    body = {"type": "about:blank",
            "title": _STATUS_TITLES.get(status, "Error"),
            "status": status, "detail": detail}
    if instance:
        body["instance"] = instance
    return JSONResponse(body, status_code=status,
                        media_type="application/problem+json")


@app.exception_handler(HTTPException)
async def _http_exc(request: Request, exc: HTTPException):
    return _problem(exc.status_code, exc.detail, str(request.url.path))


@app.exception_handler(Exception)
async def _any_exc(request: Request, exc: Exception):
    # Details go to the server log only — clients get a generic problem body.
    import logging
    logging.getLogger("transit").exception("unhandled error on %s", request.url.path)
    return _problem(500, "Internal server error", str(request.url.path))


from fastapi.exceptions import RequestValidationError  # noqa: E402


@app.exception_handler(RequestValidationError)
async def _validation_exc(request: Request, exc: RequestValidationError):
    return _problem(422, exc.errors(), str(request.url.path))


# ── Prometheus-style metrics (no dependency; text exposition format) ─────────
_metrics_lock = threading.Lock()
_req_count: dict = defaultdict(int)          # (path_template, status) -> n
_req_ms_sum: dict = defaultdict(float)       # path_template -> total ms
_started_at = time.time()


@app.middleware("http")
async def _measure(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    with _metrics_lock:
        _req_count[(path, response.status_code)] += 1
        _req_ms_sum[path] += (time.time() - t0) * 1000
    return response


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Prometheus text exposition — point Prometheus/Grafana straight here."""
    from fastapi.responses import PlainTextResponse
    L = ["# HELP transit_requests_total HTTP requests by path and status",
         "# TYPE transit_requests_total counter"]
    with _metrics_lock:
        for (path, status), n in sorted(_req_count.items()):
            L.append(f'transit_requests_total{{path="{path}",status="{status}"}} {n}')
        L.append("# HELP transit_request_ms_sum Total handler milliseconds by path")
        L.append("# TYPE transit_request_ms_sum counter")
        for path, ms in sorted(_req_ms_sum.items()):
            L.append(f'transit_request_ms_sum{{path="{path}"}} {ms:.1f}')
    L.append("# HELP transit_uptime_seconds Seconds since process start")
    L.append("# TYPE transit_uptime_seconds gauge")
    L.append(f"transit_uptime_seconds {time.time() - _started_at:.0f}")
    L.append("# HELP transit_ingested_feeds Number of ingested feeds")
    L.append("# TYPE transit_ingested_feeds gauge")
    L.append(f"transit_ingested_feeds {len(store.available_feeds())}")
    return PlainTextResponse("\n".join(L) + "\n", media_type="text/plain; version=0.0.4")


# ── meta ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"ok": True, "ingested_feeds": store.available_feeds(),
            "registered_feeds": len(_FEEDS)}


@app.get("/cities")
def cities():
    """Ingested cities with their center coordinate — the map's city picker."""
    out = []
    for fid in store.available_feeds():
        f = _FEEDS.get(fid, {})
        c = store.center(fid)
        out.append({"feed": fid, "city": f.get("city_region", fid),
                    "country": f.get("country"), "agency": f.get("agency_provider"),
                    "lat": c[0] if c else None, "lon": c[1] if c else None})
    return out


@app.get("/feeds")
def feeds(country: Optional[str] = Query(None, description="2-letter code, e.g. IT"),
          q: Optional[str] = Query(None, description="search city/agency name"),
          limit: int = Query(100, le=2000), offset: int = 0):
    """Browse EVERY registered feed (curated + world catalog) — every city and
    region the API knows about, ingested or not. Filter by country or name."""
    ingested = set(store.available_feeds())
    ql = (q or "").lower()
    out = []
    for fid, f in _FEEDS.items():
        if country and (f.get("country") or "").upper() != country.upper():
            continue
        if ql and ql not in f"{f.get('city_region','')} {f.get('agency_provider','')} {f.get('name','')}".lower():
            continue
        out.append({"feed": fid, "city": f.get("city_region"),
                    "country": f.get("country"), "agency": f.get("agency_provider"),
                    "lat": f.get("lat"), "lon": f.get("lon"),
                    "ingested": fid in ingested})
    out.sort(key=lambda x: ((x["country"] or "‾"), (x["city"] or "‾")))
    return {"total": len(out), "feeds": out[offset:offset + limit]}


@app.get("/countries")
def countries():
    """Country → feed count across the whole registry."""
    per: dict = {}
    for f in _FEEDS.values():
        c = f.get("country") or "?"
        per[c] = per.get(c, 0) + 1
    return dict(sorted(per.items(), key=lambda kv: -kv[1]))


_MAX_CONCURRENT_INGESTS = 2
_ingest_lock = threading.Lock()
# fid -> {"status": queued|running|completed|failed, "error", timestamps}
_ingest_jobs: dict = {}


def _invalidate_caches():
    """Drop every in-RAM cache so a re-ingested feed is served fresh."""
    for fn in (store.lines, store.stops, store.center,
               routing._stops, routing._footpaths, routing._day_connections):
        cache_clear = getattr(fn, "cache_clear", None)
        if cache_clear:
            cache_clear()


def _do_ingest(fid: str):
    _ingest_jobs[fid].update(status="running",
                             started_at=dt.datetime.utcnow().isoformat() + "Z")
    try:
        summary = ingest_mod.ingest(_FEEDS[fid])
        _invalidate_caches()
        _ingest_jobs[fid].update(status="completed", summary=summary)
    except Exception as e:  # noqa: BLE001
        # Safe, bounded description — full traceback goes to the server log.
        import logging
        logging.getLogger("transit").exception("ingest failed for %s", fid)
        _ingest_jobs[fid].update(status="failed",
                                 error=f"{type(e).__name__}: {str(e)[:180]}")
    finally:
        _ingest_jobs[fid]["finished_at"] = dt.datetime.utcnow().isoformat() + "Z"
        with _ingest_lock:
            _ingesting.discard(fid)


@app.post("/feeds/{feed_id}/ingest")
def ingest_feed(feed_id: str, background: BackgroundTasks,
                x_api_key: Optional[str] = Header(None),
                force: bool = Query(False, description="re-ingest even if present")):
    """Download + build a feed's artifacts in the background.

    **Disabled unless the server sets `ADMIN_KEY`** — ingest downloads and
    processes multi-MB archives, so on a public deployment it must be an
    operator-only action. With the key set, pass it as `X-API-Key`. At most
    two ingests run concurrently; `force=true` refreshes an existing feed
    (atomically — the old data serves until the new build swaps in)."""
    if not _ADMIN_KEY:
        raise HTTPException(
            403, "ingest is disabled: set ADMIN_KEY on the server and pass "
                 "X-API-Key (or run `python -m app.ingest <id>` locally)")
    if x_api_key != _ADMIN_KEY:
        raise HTTPException(401, "X-API-Key required")
    if feed_id not in _FEEDS:
        raise HTTPException(404, f"unknown feed '{feed_id}' — see /feeds")
    if feed_id in store.available_feeds() and not force:
        return {"status": "already ingested", "feed": feed_id,
                "hint": "pass ?force=true to refresh"}
    # Check-and-reserve atomically — two racing requests can't both pass.
    with _ingest_lock:
        if feed_id in _ingesting:
            return {"status": "ingest already running", "feed": feed_id,
                    "poll": f"/ingests/{feed_id}"}
        if len(_ingesting) >= _MAX_CONCURRENT_INGESTS:
            raise HTTPException(429, f"{_MAX_CONCURRENT_INGESTS} ingests already "
                                     "running — try again when one finishes")
        _ingesting.add(feed_id)
    _ingest_jobs[feed_id] = {"feed": feed_id, "status": "queued",
                             "queued_at": dt.datetime.utcnow().isoformat() + "Z"}
    background.add_task(_do_ingest, feed_id)
    return {"status": "ingest started", "feed": feed_id,
            "poll": f"/ingests/{feed_id}"}


@app.get("/ingests/{feed_id}")
def ingest_status(feed_id: str):
    """Status of an ingest started via POST /feeds/{id}/ingest:
    `queued → running → completed | failed` (with a safe error message).
    For feeds ingested outside this process (CLI), reports `completed` when
    the artifacts exist."""
    job = _ingest_jobs.get(feed_id)
    if job:
        return job
    if feed_id in store.available_feeds():
        return {"feed": feed_id, "status": "completed",
                "note": "ingested outside this process"}
    if feed_id not in _FEEDS:
        raise HTTPException(404, f"unknown feed '{feed_id}' — see /feeds")
    return {"feed": feed_id, "status": "not started"}


# ── routes & map geometry ────────────────────────────────────────────────────

@app.get("/routes")
def routes(city: str = Query(..., description="feed id, e.g. szczecin-zditm"),
           mode: Optional[str] = None):
    _require(city)
    rs = store.routes(city)
    return [r for r in rs if mode is None or r["mode"] == mode]


@app.get("/routes/{city}/{route_id}/geometry")
def route_geometry(city: str, route_id: str):
    _require(city)
    fc = store.route_geometry(city, route_id)
    if not fc["features"]:
        raise HTTPException(404, f"no geometry for route {route_id}")
    return JSONResponse(fc)


@app.get("/routes/{city}/{route_id}/stops")
def route_stops(city: str, route_id: str, direction: str = "0"):
    """Ordered stops of a route in one direction (its longest trip's calling
    pattern) — powers on-device ride detection's stop countdown."""
    _require(city)
    return schedule.route_stops(city, route_id, direction)


@app.get("/map/layers")
def map_layers(city: str = Query(...)):
    """What the map should draw, and where to fetch it."""
    _require(city)
    modes = sorted({r["mode"] for r in store.routes(city)})
    return {
        "city": city,
        "lines": {"url": f"/map/{city}/lines.geojson", "color_from": "route_color|mode_default"},
        "stops": {"url": f"/stops/nearby?city={city}", "cluster_by": "mode"},
        "modes": modes,
        "live_vehicles": _rt_vehicles_url(city) is not None,
    }


@app.get("/map/{city}/lines.geojson")
def lines_geojson(city: str):
    _require(city)
    return JSONResponse(store.lines(city))


# ── stops ────────────────────────────────────────────────────────────────────

@app.get("/stops")
def stops_all(city: str = Query(...)):
    _require(city)
    return store.stops(city)


@app.get("/stops/nearby")
def stops_nearby(city: str = Query(...),
                 lat: float = Query(...), lng: float = Query(...),
                 radius: float = Query(500, description="metres"),
                 limit: int = 50):
    _require(city)
    return store.stops_nearby(city, lat, lng, radius, limit)


@app.get("/stops/search")
def stops_search(city: str = Query(...), q: str = Query(..., min_length=2), limit: int = 12):
    _require(city)
    return schedule.search_stops(city, q, limit)


@app.get("/stops/{city}/{stop_id}/directions")
def stop_directions(city: str, stop_id: str):
    """Distinct directions at a stop (for the both-ways selector)."""
    _require(city)
    return schedule.directions(city, stop_id)


@app.get("/stops/{city}/{stop_id}/departures")
def stop_departures(city: str, stop_id: str, limit: int = 15,
                    direction: Optional[str] = None):
    """Next departures at a stop — the "My Stop" board. Live where the realtime
    feed is tracking today's trip. Optional `direction` (0/1)."""
    _require(city)
    delays = _trip_delays(city)
    return schedule.departures(city, stop_id, at=_feed_now(city),
                               limit=limit, direction=direction, delays=delays)


# ── routing & realtime ───────────────────────────────────────────────────────

@app.get("/journey")
def journey(city: str = Query(..., description="feed id, e.g. szczecin-zditm"),
            from_lat: float = Query(...), from_lon: float = Query(...),
            to_lat: float = Query(...), to_lon: float = Query(...),
            time: Optional[str] = Query(None, description="ISO departure time; default now")):
    """Plan an A→B city transit journey (walk + rides, any transfers) with live
    delays on the boarding leg where the realtime feed has them."""
    _require(city)
    when = _feed_now(city)
    if time:
        try:
            when = dt.datetime.fromisoformat(time)
        except ValueError:
            raise HTTPException(400, "bad `time` (want ISO 8601)")
    return {"city": city,
            "itineraries": routing.plan(city, from_lat, from_lon, to_lat, to_lon,
                                        when, _trip_delays(city))}


@app.get("/vehicles/live")
def vehicles_live(city: str = Query(..., description="feed id, e.g. szczecin-zditm")):
    """Live vehicle positions (moving map markers) for feeds that publish a
    GTFS-RT VehiclePosition feed. Each vehicle carries its line/mode/color
    (joined from the static GTFS) plus lat/lon and heading."""
    _require(city)
    rt_url = _rt_vehicles_url(city)
    if not rt_url:
        return {"city": city, "vehicles": []}
    try:
        return {"city": city, "vehicles": realtime.vehicles_live(city, rt_url)}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"realtime feed unavailable: {e}")


@app.get("/vehicles/stream")
async def vehicles_stream(city: str = Query(..., description="feed id"),
                          interval: float = Query(5.0, ge=2.0, le=30.0)):
    """**Server-Sent Events** stream of live vehicle positions — subscribe once
    and receive a fresh frame every `interval` seconds; no polling code needed:

        const es = new EventSource("/vehicles/stream?city=szczecin-zditm");
        es.onmessage = (e) => drawVehicles(JSON.parse(e.data));

    Each event's `data:` is the same JSON as GET /vehicles/live. Ends only when
    the client disconnects."""
    _require(city)
    rt_url = _rt_vehicles_url(city)
    if not rt_url:
        raise HTTPException(404, f"feed '{city}' publishes no GTFS-RT vehicles")

    import asyncio

    async def gen():
        while True:
            try:
                vehicles = await asyncio.to_thread(realtime.vehicles_live, city, rt_url)
                payload = json.dumps({"city": city, "count": len(vehicles),
                                      "vehicles": vehicles}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            except Exception as e:  # noqa: BLE001 — keep the stream alive
                yield f"event: error\ndata: {json.dumps(str(e)[:200])}\n\n"
            await asyncio.sleep(interval)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


# ── helpers ──────────────────────────────────────────────────────────────────

def _require(city: str):
    if city not in store.available_feeds():
        raise HTTPException(404, f"feed '{city}' not ingested; run `python -m app.ingest {city}`")


def _rt_vehicles_url(city: str) -> Optional[str]:
    return _FEEDS.get(city, {}).get("gtfs_rt_vehicles_url")


def _trip_delays(city: str) -> dict[str, int]:
    """Live trip delays from the feed's GTFS-RT TripUpdate feed, or {} if none."""
    trips_url = _FEEDS.get(city, {}).get("gtfs_rt_trips_url")
    if not trips_url:
        return {}
    try:
        return realtime.trip_delays(city, trips_url)
    except Exception:
        return {}


def _feed_timezone(city: str) -> Optional[str]:
    """Feed timezone: registry entry first, else agency.txt captured at ingest
    (summary.json) — world-catalog feeds get theirs from the GTFS itself."""
    tz = _FEEDS.get(city, {}).get("timezone")
    if tz:
        return tz
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "data",
                               city, "summary.json")) as fh:
            return json.load(fh).get("timezone")
    except Exception:  # noqa: BLE001
        return None


def _feed_now(city: str) -> dt.datetime:
    """Current wall-clock time in the feed's own timezone — GTFS times are local,
    so a server in another timezone must not use its own clock."""
    tz = _feed_timezone(city)
    if tz and ZoneInfo:
        try:
            return dt.datetime.now(ZoneInfo(tz)).replace(tzinfo=None)
        except Exception:  # noqa: BLE001
            pass
    return dt.datetime.now()
