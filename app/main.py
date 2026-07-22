"""
City-transit read API — map geometry, stops, live vehicles and A→B routing.

Serves the ingested GTFS artifacts to a map frontend / mobile app. Turns
official GTFS Static feeds into per-city GeoJSON line layers (real route colors)
and stop lists, plans door-to-door city journeys (walk + rides + transfers) with
a stdlib Connection Scan router, and overlays live positions/delays where a feed
publishes GTFS-Realtime. No API keys, no database — artifacts are flat files.

    pip install -r requirements.txt
    python -m app.ingest szczecin-zditm      # download + build artifacts
    uvicorn app.main:app --reload
"""
import datetime as dt
import json
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

from . import realtime, routing, schedule, store

app = FastAPI(title="City Transit API", version="1.0.0")

_registry = json.load(open(os.path.join(os.path.dirname(__file__), "..", "feeds.json")))
_FEEDS = {f["id"]: f for f in _registry["feeds"]}


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


def _feed_now(city: str) -> dt.datetime:
    """Current wall-clock time in the feed's own timezone — GTFS times are local,
    so a server in another timezone must not use its own clock."""
    tz = _FEEDS.get(city, {}).get("timezone")
    if tz and ZoneInfo:
        try:
            return dt.datetime.now(ZoneInfo(tz)).replace(tzinfo=None)
        except Exception:  # noqa: BLE001
            pass
    return dt.datetime.now()
