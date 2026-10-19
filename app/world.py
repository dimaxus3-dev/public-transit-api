"""World coverage: the 100 largest cities vs. the keyless world registry.

A city counts as covered when at least one feed in feeds_world.json is centred
within ``RADIUS_KM`` of it, so a match can include neighbouring agencies. A
city is "ingested" when a locally ingested feed's stop centre lies within the
same radius. Each city is also projected onto the 1600x700 Equal Earth frame
of ``static/world-land.svg`` so the page can place its dots. Stdlib only.
"""

from __future__ import annotations

import functools
import json
import math
import os

from . import store
from .paths import registry_file

RADIUS_KM = 45.0
MAP_W, MAP_H = 1600, 700

# Equal Earth (Šavrič, Patterson & Jenny 2018) and the affine fit of
# static/world-land.svg's 1600x700 frame.
_A1, _A2, _A3, _A4 = 1.340264, -0.081106, 0.000893, 0.003796
_KX, _OX, _KY, _OY = 295.5967, 800.0529, -295.7406, 386.4207

_CITIES_FILE = os.path.join(os.path.dirname(__file__), "world_cities.json")


def project(lat: float, lon: float) -> tuple[float, float]:
    """Equal Earth position of (lat, lon) in world-land.svg pixels."""
    t = math.asin(math.sqrt(3) / 2 * math.sin(math.radians(lat)))
    t2 = t * t
    t6 = t2 * t2 * t2
    x = 2 * math.sqrt(3) * math.radians(lon) * math.cos(t) / (
        3 * (9 * _A4 * t6 * t2 + 7 * _A3 * t6 + 3 * _A2 * t2 + _A1)
    )
    y = t * (_A4 * t6 * t2 + _A3 * t6 + _A2 * t2 + _A1)
    return _KX * x + _OX, _KY * y + _OY


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


@functools.lru_cache(maxsize=1)
def _cities() -> tuple[str, list[dict]]:
    with open(_CITIES_FILE, encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc["source"], doc["cities"]


@functools.lru_cache(maxsize=1)
def _world_feeds() -> list[dict]:
    path = registry_file("feeds_world.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        feeds = json.load(fh)["feeds"]
    return [f for f in feeds if isinstance(f.get("lat"), (int, float)) and isinstance(f.get("lon"), (int, float))]


def _ingested_centres() -> list[tuple[str, float, float]]:
    out = []
    for fid in store.available_feeds():
        try:
            c = store.center(fid)
        except (OSError, ValueError):
            continue
        if c:
            out.append((fid, c[0], c[1]))
    return out


def build() -> dict:
    """Coverage of the top-100 cities, ready for the /world page."""
    source, cities = _cities()
    feeds = _world_feeds()
    ingested = _ingested_centres()
    out = []
    for c in cities:
        near = []
        for f in feeds:
            d = _haversine_km(c["lat"], c["lon"], f["lat"], f["lon"])
            if d <= RADIUS_KM:
                near.append((d, f))
        near.sort(key=lambda p: (p[0], p[1]["id"]))
        local = [fid for fid, la, lo in ingested if _haversine_km(c["lat"], c["lon"], la, lo) <= RADIUS_KM]
        x, y = project(c["lat"], c["lon"])
        out.append(
            {
                **c,
                "x": round(x, 1),
                "y": round(y, 1),
                "feeds": [
                    {"id": f["id"], "agency": f.get("agency_provider") or f.get("name") or f["id"], "km": round(d, 1)}
                    for d, f in near
                ],
                "ingested": local,
            }
        )
    covered = sum(1 for c in out if c["feeds"])
    return {
        "radius_km": RADIUS_KM,
        "map": {"width": MAP_W, "height": MAP_H, "projection": "Equal Earth"},
        "source": source,
        "summary": {
            "cities": len(out),
            "covered": covered,
            "uncovered": len(out) - covered,
            "feeds": sum(len(c["feeds"]) for c in out),
            "ingested": sum(1 for c in out if c["ingested"]),
        },
        "cities": out,
    }
