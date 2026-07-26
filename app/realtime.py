"""
GTFS-Realtime vehicle positions — live moving markers for the map.

Some agencies publish a `gtfs-rt-vehicles.pb` (a GTFS-Realtime FeedMessage of
VehiclePosition entities). Szczecin's ZDiTM feed is verified live: ~180 trams &
buses with lat/lon + bearing + vehicle label, every few seconds.

The RT feed only carries a `trip_id` (its TripDescriptor omits route_id), so we
join each vehicle to its line/mode/color through the static `gtfs.sqlite` the
ingest already built. Results are cached briefly so many app clients (and rapid
polls) don't hammer the agency's endpoint.

Kept dependency-free to match the rest of the backend: the protobuf wire format
is decoded by hand — we only need a handful of scalar fields, no schema needed.
"""

from __future__ import annotations

import os
import sqlite3
import struct
import time
import urllib.request
from typing import Optional

from .paths import DATA_DIR  # noqa: E402

# --- minimal protobuf wire reader (stdlib only) -----------------------------
# We decode just the GTFS-RT fields we use, so a tiny generic reader suffices.


def _read_varint(b: bytes, i: int) -> tuple[int, int]:
    result = shift = 0
    while True:
        x = b[i]
        i += 1
        result |= (x & 0x7F) << shift
        if not x & 0x80:
            return result, i
        shift += 7


def _fields(b: bytes) -> dict[int, list]:
    """Parse a protobuf message into {field_number: [values]}. Length-delimited
    values stay as raw bytes (decode further on demand); varints as ints;
    fixed32 as bytes (for floats)."""
    out: dict[int, list] = {}
    i, n = 0, len(b)
    while i < n:
        key, i = _read_varint(b, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:  # varint
            v, i = _read_varint(b, i)
        elif wt == 2:  # length-delimited
            ln, i = _read_varint(b, i)
            v = b[i : i + ln]
            i += ln
        elif wt == 5:  # fixed32
            v = b[i : i + 4]
            i += 4
        elif wt == 1:  # fixed64
            v = b[i : i + 8]
            i += 8
        else:
            raise ValueError(f"unsupported wire type {wt}")
        out.setdefault(fn, []).append(v)
    return out


def _f32(v: bytes) -> Optional[float]:
    return struct.unpack("<f", v)[0] if len(v) == 4 else None


def _str(v: bytes) -> str:
    return v.decode("utf-8", "replace")


# GTFS-RT field numbers used below (from gtfs-realtime.proto):
#   FeedMessage.entity = 2
#   FeedEntity.id = 1, .vehicle = 4
#   VehiclePosition.trip = 1, .position = 2, .timestamp = 5, .vehicle = 8
#   TripDescriptor.trip_id = 1
#   Position.latitude = 1, .longitude = 2, .bearing = 3
#   VehicleDescriptor.id = 1, .label = 2


_OCCUPANCY = {
    0: "empty",
    1: "many_seats",
    2: "few_seats",
    3: "standing_room",
    4: "crushed_standing",
    5: "full",
    6: "not_accepting_passengers",
}


def _decode_vehicles(pb: bytes) -> list[dict]:
    msg = _fields(pb)
    out: list[dict] = []
    for eb in msg.get(2, []):
        e = _fields(eb)
        if 4 not in e:  # not a VehiclePosition entity
            continue
        vp = _fields(e[4][0])
        pos = _fields(vp[2][0]) if 2 in vp else {}
        lat = _f32(pos[1][0]) if 1 in pos else None
        lon = _f32(pos[2][0]) if 2 in pos else None
        if lat is None or lon is None:
            continue
        trip = _fields(vp[1][0]) if 1 in vp else {}
        veh = _fields(vp[8][0]) if 8 in vp else {}
        out.append(
            {
                "id": _str(e[1][0]) if 1 in e else "",
                "trip_id": _str(trip[1][0]) if 1 in trip else None,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "bearing": round(_f32(pos[3][0]), 1) if 3 in pos else None,
                "label": (_str(veh[2][0]) if 2 in veh else (_str(veh[1][0]) if 1 in veh else None)),
                "timestamp": int.from_bytes(vp[5][0], "little")
                if 5 in vp and isinstance(vp[5][0], (bytes, bytearray))
                else (vp[5][0] if 5 in vp else None),
                "occupancy": _OCCUPANCY.get(vp[9][0])
                if 9 in vp and isinstance(vp[9][0], int)
                else None,
            }
        )
    return out


# --- trip -> route resolution (via the static gtfs.sqlite) ------------------


def _resolve_routes(feed_id: str, trip_ids: set[str]) -> dict[str, dict]:
    """Map each trip_id to its line's {route, mode, color} using the ingested
    SQLite. Returns only the trips we ask for (one indexed query)."""
    path = os.path.join(DATA_DIR, feed_id, "gtfs.sqlite")
    if not trip_ids or not os.path.exists(path):
        return {}
    db = sqlite3.connect(path)
    try:
        out: dict[str, dict] = {}
        ids = list(trip_ids)
        for i in range(0, len(ids), 400):  # SQLite param limit safety
            chunk = ids[i : i + 400]
            q = (
                "SELECT t.trip_id, r.short_name, r.mode, r.color, t.headsign "
                "FROM trips t LEFT JOIN routes r ON r.route_id = t.route_id "
                f"WHERE t.trip_id IN ({','.join('?' * len(chunk))})"
            )
            for tid, short, mode, color, headsign in db.execute(q, chunk):
                out[tid] = {
                    "route": short,
                    "mode": mode or "bus",
                    "color": color,
                    "headsign": headsign or "",
                }
        return out
    finally:
        db.close()


# --- public API (cached) ----------------------------------------------------

_CACHE: dict[str, tuple[float, list[dict]]] = {}
_TTL = 4.0  # seconds — agency feeds refresh every few seconds
_FAIL_BACKOFF = 30.0  # after a fetch failure, don't re-try the upstream for this long
_STALE_OK = 60.0  # serve a stale frame this old rather than fail
_fail_at: dict[str, float] = {}


def vehicles_live(feed_id: str, rt_url: str) -> list[dict]:
    """Live vehicles for a feed as [{id, route, mode, color, lat, lon, bearing,
    label, headsign, trip_id, timestamp}], newest cached within _TTL seconds.

    Degrades gracefully when the protobuf stream stops answering: a recent
    stale frame (< _STALE_OK) is served instead, upstream is not re-tried for
    _FAIL_BACKOFF seconds (so requests fail/serve-stale instantly instead of
    each hanging on the socket timeout), and only with no usable frame at all
    does it raise (the API then 502s)."""
    now = time.time()
    hit = _CACHE.get(feed_id)
    if hit and now - hit[0] < _TTL:
        return hit[1]

    if now - _fail_at.get(feed_id, float("-inf")) < _FAIL_BACKOFF:
        if hit and now - hit[0] < _STALE_OK:
            return hit[1]
        raise RuntimeError("realtime feed unavailable (in backoff)")

    try:
        req = urllib.request.Request(rt_url, headers={"User-Agent": "public-transit-api/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            pb = r.read()
    except Exception:
        _fail_at[feed_id] = now
        if hit and now - hit[0] < _STALE_OK:
            return hit[1]
        raise
    _fail_at.pop(feed_id, None)

    vehicles = _decode_vehicles(pb)
    routes = _resolve_routes(feed_id, {v["trip_id"] for v in vehicles if v["trip_id"]})
    for v in vehicles:
        meta = routes.get(v["trip_id"] or "", {})
        v["route"] = meta.get("route")
        v["mode"] = meta.get("mode", "bus")
        v["color"] = meta.get("color")
        v["headsign"] = meta.get("headsign", "")

    _CACHE[feed_id] = (now, vehicles)
    return vehicles


# --- live delays (TripUpdate feed) ------------------------------------------

_DELAY_CACHE: dict[str, tuple[float, dict[str, int]]] = {}


def _signed(v: int) -> int:
    """Protobuf int32 delay is sign-extended to 64 bits when negative."""
    return v - (1 << 64) if v >= (1 << 63) else v


_delay_fail_at: dict[str, float] = {}
_STATUS = {0: "scheduled", 1: "added", 2: "unscheduled", 3: "canceled"}


def _decode_trip_states(pb: bytes) -> dict:
    """Full TripUpdate decode → the internal realtime model:

        {"timestamp": <feed header ts>, "trips": {trip_id: {
            "status": scheduled|added|unscheduled|canceled,
            "delay": <trip-level seconds>,
            "stops": {stop_id: {"arr": s, "dep": s, "skipped": bool}}}}}

    Field numbers per gtfs-realtime.proto: FeedMessage.header=1 (.timestamp=3),
    entity=2; FeedEntity.trip_update=3; TripUpdate.trip=1 (.trip_id=1,
    .schedule_relationship=4), .stop_time_update=2 (.stop_sequence=1,
    .arrival=2, .departure=3, .stop_id=4, .schedule_relationship=5:SKIPPED=1),
    .delay=5; StopTimeEvent.delay=1."""
    msg = _fields(pb)
    header = _fields(msg[1][0]) if 1 in msg else {}
    ts = header.get(3, [None])[0]
    trips: dict[str, dict] = {}
    for eb in msg.get(2, []):
        e = _fields(eb)
        if 3 not in e:
            continue
        tu = _fields(e[3][0])
        trip = _fields(tu[1][0]) if 1 in tu else {}
        tid = _str(trip[1][0]) if 1 in trip else None
        if not tid:
            continue
        sched_rel = trip.get(4, [0])[0]
        state: dict = {
            "status": _STATUS.get(sched_rel if isinstance(sched_rel, int) else 0, "scheduled"),
            "delay": None,
            "stops": {},
        }
        if 5 in tu and isinstance(tu[5][0], int):
            state["delay"] = _signed(tu[5][0])
        for stu_b in tu.get(2, []):
            stu = _fields(stu_b)
            sid = _str(stu[4][0]) if 4 in stu else None
            if sid is None:
                continue
            upd = {"arr": None, "dep": None, "skipped": False}
            if 5 in stu and isinstance(stu[5][0], int) and stu[5][0] == 1:
                upd["skipped"] = True
            for field, key in ((2, "arr"), (3, "dep")):
                if field in stu:
                    ev = _fields(stu[field][0])
                    if 1 in ev and isinstance(ev[1][0], int):
                        upd[key] = _signed(ev[1][0])
            state["stops"][sid] = upd
        if state["delay"] is None:
            first = next(
                (
                    u["dep"] if u["dep"] is not None else u["arr"]
                    for u in state["stops"].values()
                    if not u["skipped"] and (u["dep"] is not None or u["arr"] is not None)
                ),
                None,
            )
            state["delay"] = first or 0
        trips[tid] = state
    return {"timestamp": ts if isinstance(ts, int) else None, "trips": trips}


_STATE_CACHE: dict[str, tuple[float, dict]] = {}


def trip_states(feed_id: str, rt_trips_url: str) -> dict:
    """Full realtime state (cancellations, skipped stops, per-stop delays,
    feed timestamp). Same cache/backoff discipline as trip_delays; returns
    {"timestamp": None, "trips": {}} instead of ever raising."""
    now = time.time()
    hit = _STATE_CACHE.get(feed_id)
    if hit and now - hit[0] < _TTL:
        return hit[1]
    if now - _delay_fail_at.get(feed_id, float("-inf")) < _FAIL_BACKOFF:
        return hit[1] if hit else {"timestamp": None, "trips": {}}
    try:
        req = urllib.request.Request(rt_trips_url, headers={"User-Agent": "public-transit-api/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            pb = r.read()
        _delay_fail_at.pop(feed_id, None)
    except Exception:
        _delay_fail_at[feed_id] = now
        return hit[1] if hit else {"timestamp": None, "trips": {}}
    try:
        state = _decode_trip_states(pb)
    except Exception:
        state = {"timestamp": None, "trips": {}}
    _STATE_CACHE[feed_id] = (now, state)
    return state


def trip_delays(feed_id: str, rt_trips_url: str) -> dict[str, int]:
    """Map trip_id -> current delay in seconds, from the GTFS-RT TripUpdate feed.
    A representative per-trip delay (TripUpdate.delay, else the first stop's
    departure/arrival delay). Cached within _TTL.

    Never raises: on upstream failure the last known delays (or {}) come back,
    so departure boards and journeys silently fall back to the static
    timetable. A failed upstream is left alone for _FAIL_BACKOFF seconds —
    one slow request per backoff window, everyone else answers instantly."""
    now = time.time()
    hit = _DELAY_CACHE.get(feed_id)
    if hit and now - hit[0] < _TTL:
        return hit[1]
    if now - _delay_fail_at.get(feed_id, float("-inf")) < _FAIL_BACKOFF:
        return hit[1] if hit else {}
    try:
        req = urllib.request.Request(rt_trips_url, headers={"User-Agent": "public-transit-api/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            pb = r.read()
        _delay_fail_at.pop(feed_id, None)
    except Exception:
        _delay_fail_at[feed_id] = now
        return hit[1] if hit else {}

    out: dict[str, int] = {}
    for eb in _fields(pb).get(2, []):
        e = _fields(eb)
        if 3 not in e:  # FeedEntity.trip_update = 3
            continue
        tu = _fields(e[3][0])
        trip = _fields(tu[1][0]) if 1 in tu else {}
        tid = _str(trip[1][0]) if 1 in trip else None
        if not tid:
            continue
        delay: Optional[int] = None
        if 5 in tu and isinstance(tu[5][0], int):  # TripUpdate.delay
            delay = _signed(tu[5][0])
        else:
            for stu in tu.get(2, []):  # first stop with a delay
                st = _fields(stu)
                ev = _fields(st[3][0]) if 3 in st else (_fields(st[2][0]) if 2 in st else {})
                if 1 in ev and isinstance(ev[1][0], int):
                    delay = _signed(ev[1][0])
                    break
        out[tid] = delay or 0
    _DELAY_CACHE[feed_id] = (now, out)
    return out
