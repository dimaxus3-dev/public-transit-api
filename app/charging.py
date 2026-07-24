"""EV charging stations — Open Charge Map (global) and NREL (North America).

Both providers are free but key-gated, so this module activates per key:

    OCM_API_KEY     openchargemap.org → My Profile → my apps → Register An
                    Application. Data is CC BY 4.0 — the response carries the
                    required attribution string; keep it visible in your UI.
    NREL_API_KEY    free at api.data.gov (1000 req/h).
    NREL_API_BASE   default https://developer.nlr.gov — NREL moved off
                    developer.nrel.gov in May 2026; override if it moves again.

Responses are cached (2 min TTL) and OCM is never hammered: one upstream call
per rounded-coordinate cell per TTL window, per their fair-use policy.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.parse
import urllib.request

OCM_KEY = os.environ.get("OCM_API_KEY", "")
NREL_KEY = os.environ.get("NREL_API_KEY", "")
NREL_BASE = os.environ.get("NREL_API_BASE", "https://developer.nlr.gov")

OCM_ATTRIBUTION = "Charging data © Open Charge Map contributors (CC BY 4.0) — openchargemap.org"

_TTL = 120.0
_cache: dict = {}
_lock = threading.Lock()


def available() -> dict:
    return {"ocm": bool(OCM_KEY), "nrel": bool(NREL_KEY)}


def _get(url: str, headers: dict, timeout: int = 20):
    req = urllib.request.Request(url, headers={"User-Agent": "public-transit-api/1.0", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _cached(key):
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < _TTL:
            return hit[1]
    return None


def _store(key, value):
    with _lock:
        _cache[key] = (time.time(), value)
    return value


def ocm_nearby(lat: float, lng: float, radius_km: float = 5, limit: int = 25) -> dict:
    """Open Charge Map POIs around a point (global coverage, ~300k sites)."""
    key = ("ocm", round(lat, 3), round(lng, 3), radius_km, limit)
    hit = _cached(key)
    if hit is not None:
        return hit
    url = "https://api.openchargemap.io/v3/poi/?" + urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lng,
            "distance": radius_km,
            "distanceunit": "km",
            "maxresults": limit,
            "compact": "true",
            "verbose": "false",
        }
    )
    pois = _get(url, {"X-API-Key": OCM_KEY})
    out = []
    for p in pois:
        addr = p.get("AddressInfo") or {}
        conns = p.get("Connections") or []
        out.append(
            {
                "id": p.get("ID"),
                "name": addr.get("Title"),
                "lat": addr.get("Latitude"),
                "lon": addr.get("Longitude"),
                "address": ", ".join(x for x in (addr.get("AddressLine1"), addr.get("Town")) if x),
                "operator_id": p.get("OperatorID"),
                "connections": [
                    {
                        "type_id": c.get("ConnectionTypeID"),
                        "kw": c.get("PowerKW"),
                        "quantity": c.get("Quantity"),
                    }
                    for c in conns
                ],
                "max_kw": max((c.get("PowerKW") or 0 for c in conns), default=None),
            }
        )
    return _store(
        key,
        {"provider": "openchargemap", "attribution": OCM_ATTRIBUTION, "stations": out},
    )


def nrel_nearby(lat: float, lng: float, radius_km: float = 5, limit: int = 25) -> dict:
    """NREL alternative-fuel stations near a point (US/Canada, EV only)."""
    key = ("nrel", round(lat, 3), round(lng, 3), radius_km, limit)
    hit = _cached(key)
    if hit is not None:
        return hit
    url = f"{NREL_BASE}/api/alt-fuel-stations/v1/nearest.json?" + urllib.parse.urlencode(
        {
            "api_key": NREL_KEY,
            "latitude": lat,
            "longitude": lng,
            "radius": radius_km * 0.621371,  # NREL wants miles
            "fuel_type": "ELEC",
            "limit": limit,
            "status": "E",
        }
    )
    data = _get(url, {})
    out = [
        {
            "id": s.get("id"),
            "name": s.get("station_name"),
            "lat": s.get("latitude"),
            "lon": s.get("longitude"),
            "address": ", ".join(x for x in (s.get("street_address"), s.get("city")) if x),
            "network": s.get("ev_network"),
            "connectors": s.get("ev_connector_types"),
            "dc_fast": s.get("ev_dc_fast_num"),
            "level2": s.get("ev_level2_evse_num"),
        }
        for s in data.get("fuel_stations", [])
    ]
    return _store(key, {"provider": "nrel", "stations": out})
