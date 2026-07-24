"""
In-memory store over the ingested artifacts. Loads lines.geojson + stops.json
per feed and answers the read queries the API needs. Swap this module for a
PostGIS-backed one to scale (same interface); the ingest artifacts don't change.
"""
from __future__ import annotations
import json, math, os, re, functools

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _feed_dir(feed_id: str) -> str:
    # feed_id comes straight from a query parameter — constrain it to the
    # slug alphabet so "../.." can never leave DATA_DIR.
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", feed_id):
        raise FileNotFoundError(f"bad feed id: {feed_id!r}")
    return os.path.join(DATA_DIR, feed_id)


def available_feeds() -> list[str]:
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(d for d in os.listdir(DATA_DIR)
                  if os.path.exists(os.path.join(DATA_DIR, d, "lines.geojson")))


@functools.lru_cache(maxsize=32)
def lines(feed_id: str) -> dict:
    with open(os.path.join(_feed_dir(feed_id), "lines.geojson"), encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=32)
def stops(feed_id: str) -> list[dict]:
    with open(os.path.join(_feed_dir(feed_id), "stops.json"), encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=32)
def center(feed_id: str) -> tuple[float, float] | None:
    """Median stop coordinate — a robust 'where is this feed' point clients
    uses to auto-select the city nearest the user."""
    pts = [(s["lat"], s["lon"]) for s in stops(feed_id) if s.get("lat") and s.get("lon")]
    if not pts:
        return None
    lats = sorted(p[0] for p in pts)
    lons = sorted(p[1] for p in pts)
    return (lats[len(lats) // 2], lons[len(lons) // 2])


def routes(feed_id: str) -> list[dict]:
    """Distinct routes (collapsing the per-direction line features)."""
    seen, out = set(), []
    for feat in lines(feed_id)["features"]:
        p = feat["properties"]
        if p["route_id"] in seen:
            continue
        seen.add(p["route_id"])
        out.append({k: p[k] for k in ("route_id", "short_name", "long_name", "mode", "color", "text_color")})
    return sorted(out, key=lambda r: (r["mode"], r["short_name"]))


def route_geometry(feed_id: str, route_id: str) -> dict:
    feats = [f for f in lines(feed_id)["features"] if f["properties"]["route_id"] == route_id]
    return {"type": "FeatureCollection", "features": feats}


def _haversine(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def stops_nearby(feed_id: str, lat: float, lon: float, radius_m: float, limit: int = 50) -> list[dict]:
    out = []
    for s in stops(feed_id):
        d = _haversine(lat, lon, s["lat"], s["lon"])
        if d <= radius_m:
            out.append({**s, "distance_m": round(d)})
    out.sort(key=lambda s: s["distance_m"])
    return out[:limit]
