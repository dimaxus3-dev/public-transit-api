"""Shared mobility (GBFS) — scooters, bikes, mopeds, live from the operators.

GBFS (General Bikeshare Feed Specification) is the open standard published by
1500+ sharing systems worldwide. Every system exposes an auto-discovery
`gbfs.json` that lists its sub-feeds; the ones we read:

    station_information + station_status   docked systems (city bikes)
    free_bike_status / vehicle_status      dockless vehicles (scooters), with
                                           battery level and range

Same resilience pattern as GTFS-RT: short TTL cache, failure backoff, stale
frames served briefly during outages. stdlib only.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.request

from .paths import registry_file

_TTL = 15.0  # GBFS ttl is typically 10-60 s
_FAIL_BACKOFF = 60.0
_STALE_OK = 120.0

_cache: dict = {}
_fail_at: dict = {}
_lock = threading.Lock()

_registry: dict = {}


def systems() -> dict:
    """system_id -> registry entry (loaded once from feeds_gbfs.json)."""
    global _registry
    if not _registry:
        path = registry_file("feeds_gbfs.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                _registry = {s["system_id"]: s for s in json.load(fh)["systems"]}
    return _registry


def _get(url: str, timeout: int = 12) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "public-transit-api/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _discover(root: dict) -> dict:
    """name -> url from a v1/v2 (data.<lang>.feeds) or v3 (data.feeds) discovery."""
    data = root.get("data") or {}
    feeds = data.get("feeds")
    if feeds is None:  # v1/v2: language-keyed
        for lang in list(data.values()):
            if isinstance(lang, dict) and "feeds" in lang:
                feeds = lang["feeds"]
                break
    return {f["name"]: f["url"] for f in (feeds or [])}


def snapshot(system_id: str) -> dict:
    """Live stations + vehicles for one system, cached/backed-off.

    Returns {"system": …, "stations": […], "vehicles": […]} where stations
    carry availability and vehicles carry battery/range where published."""
    meta = systems().get(system_id)
    if not meta:
        raise KeyError(system_id)

    now = time.time()
    with _lock:
        hit = _cache.get(system_id)
        if hit and now - hit[0] < _TTL:
            return hit[1]
        if now - _fail_at.get(system_id, float("-inf")) < _FAIL_BACKOFF:
            if hit and now - hit[0] < _STALE_OK:
                return hit[1]
            raise RuntimeError("GBFS system unavailable (in backoff)")

    try:
        by = _discover(_get(meta["url"]))

        stations: dict[str, dict] = {}
        if "station_information" in by:
            for st in _get(by["station_information"])["data"].get("stations", []):
                stations[str(st.get("station_id"))] = {
                    "id": str(st.get("station_id")),
                    "name": st.get("name"),
                    "lat": st.get("lat"),
                    "lon": st.get("lon"),
                    "capacity": st.get("capacity"),
                }
        if "station_status" in by and stations:
            for st in _get(by["station_status"])["data"].get("stations", []):
                s = stations.get(str(st.get("station_id")))
                if s:
                    s["bikes_available"] = st.get(
                        "num_bikes_available", st.get("num_vehicles_available")
                    )
                    s["docks_available"] = st.get("num_docks_available")
                    s["renting"] = bool(st.get("is_renting", 1))

        vehicles = []
        v_url = by.get("free_bike_status") or by.get("vehicle_status")
        if v_url:
            raw = _get(v_url)["data"]
            for v in raw.get("bikes") or raw.get("vehicles") or []:
                if v.get("lat") is None or v.get("lon") is None:
                    continue
                battery = v.get("current_fuel_percent")
                vehicles.append(
                    {
                        "id": v.get("bike_id") or v.get("vehicle_id"),
                        "lat": v.get("lat"),
                        "lon": v.get("lon"),
                        "battery": round(battery * 100) if battery is not None else None,
                        "range_m": v.get("current_range_meters"),
                        "type": v.get("vehicle_type_id"),
                        "reserved": bool(v.get("is_reserved")),
                        "disabled": bool(v.get("is_disabled")),
                    }
                )
    except Exception:
        with _lock:
            _fail_at[system_id] = now
            hit = _cache.get(system_id)
            if hit and now - hit[0] < _STALE_OK:
                return hit[1]
        raise

    out = {
        "system": {k: meta[k] for k in ("system_id", "name", "location", "country")},
        "stations": sorted(stations.values(), key=lambda s: s["name"] or ""),
        "vehicles": vehicles,
    }
    with _lock:
        _fail_at.pop(system_id, None)
        _cache[system_id] = (now, out)
    return out
