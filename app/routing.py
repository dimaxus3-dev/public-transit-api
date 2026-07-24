"""
City transit journey planning — a Connection Scan Algorithm (CSA) over the
ingested GTFS. Given an origin/destination coordinate and a departure time it
returns the earliest-arrival itinerary with any number of transfers: walk →
ride → (transfer) → ride → walk, each ride leg carrying its real line, board /
alight stops and intermediate stops.

CSA is the simplest efficient GTFS router: build the day's "connections" (each
consecutive stop-time pair of an active trip) sorted by departure time, then a
single linear scan computes the earliest arrival at every stop. It's stdlib-only
and fast — an active Szczecin day is ~150k connections, scanned in well under a
second. Live delays are layered on by realtime.trip_delays().
"""
from __future__ import annotations
import datetime as dt
import functools
import math
import os
import sqlite3

from . import schedule

DATA_DIR = schedule.DATA_DIR
WALK_SPEED = 1.3            # m/s (~4.7 km/h)
MAX_ORIGIN_WALK = 900.0    # m — how far we'll walk to a first/last stop
TRANSFER_RADIUS = 250.0    # m — stops within this are walk-transferable
MIN_TRANSFER = 45          # s — floor on any walking transfer
INF = 10 ** 9


def _db(feed_id: str) -> sqlite3.Connection | None:
    path = os.path.join(DATA_DIR, feed_id, "gtfs.sqlite")
    return sqlite3.connect(path) if os.path.exists(path) else None


def _haversine(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


@functools.lru_cache(maxsize=32)
def _stops(feed_id: str) -> dict[str, tuple[str, float, float]]:
    db = _db(feed_id)
    if not db:
        return {}
    out = {sid: (name, lat, lon)
           for sid, name, lat, lon in db.execute("SELECT stop_id, name, lat, lon FROM stops")}
    db.close()
    return out


@functools.lru_cache(maxsize=32)
def _footpaths(feed_id: str) -> dict[str, list[tuple[str, int]]]:
    """Walkable transfers between nearby stops (grid-bucketed so we don't do a
    full O(n^2) sweep). Built once per feed."""
    stops = _stops(feed_id)
    cell = TRANSFER_RADIUS / 111_000.0       # ~degrees for the radius
    grid: dict[tuple[int, int], list[str]] = {}
    for sid, (_, lat, lon) in stops.items():
        grid.setdefault((int(lat / cell), int(lon / cell)), []).append(sid)
    fp: dict[str, list[tuple[str, int]]] = {}
    for sid, (_, lat, lon) in stops.items():
        gx, gy = int(lat / cell), int(lon / cell)
        near: list[tuple[str, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for other in grid.get((gx + dx, gy + dy), ()):
                    if other == sid:
                        continue
                    _, olat, olon = stops[other]
                    d = _haversine(lat, lon, olat, olon)
                    if d <= TRANSFER_RADIUS:
                        near.append((other, max(MIN_TRANSFER, int(d / WALK_SPEED))))
        if near:
            fp[sid] = near
    return fp


# A connection: (dep_sec, arr_sec, dep_stop, arr_stop, trip_id, seq)
@functools.lru_cache(maxsize=32)
def _day_connections(feed_id: str, date_key: str):
    """Sorted connections + per-trip metadata for one service day. `date_key` is
    YYYYMMDD; cached so repeated queries on the same day are instant."""
    db = _db(feed_id)
    if not db:
        return [], {}, {}
    day = dt.datetime.strptime(date_key, "%Y%m%d").date()
    svc = schedule._active_services(db, day)
    if not svc:
        db.close()
        return [], {}, {}
    ph = ",".join("?" * len(svc))
    rows = db.execute(f"""
        SELECT st.trip_id, st.stop_id, st.dep_sec, st.seq,
               r.short_name, r.mode, r.color, t.headsign
        FROM stop_times st
        JOIN trips t ON st.trip_id = t.trip_id
        JOIN routes r ON t.route_id = r.route_id
        WHERE t.service_id IN ({ph})
        ORDER BY st.trip_id, st.seq
    """, list(svc))
    trip_meta: dict[str, dict] = {}
    per_trip: dict[str, list] = {}
    for tid, sid, dep, seq, short, mode, color, head in rows:
        per_trip.setdefault(tid, []).append((seq, sid, dep))
        if tid not in trip_meta:
            trip_meta[tid] = {"route": short, "mode": mode or "bus",
                              "color": color, "headsign": head or ""}
    connections = []
    trip_stops: dict[str, list] = {}          # trip_id -> ordered [(seq, stop_id)]
    for tid, seq_rows in per_trip.items():
        seq_rows.sort()
        trip_stops[tid] = [(seq, sid) for seq, sid, _ in seq_rows]
        for i in range(len(seq_rows) - 1):
            _, s_stop, s_dep = seq_rows[i]
            _, e_stop, e_dep = seq_rows[i + 1]
            if e_dep < s_dep:                 # guard against bad data
                continue
            # store the alight seq so a ride leg can slice its own stop range
            connections.append((s_dep, e_dep, s_stop, e_stop, tid, seq_rows[i][0], seq_rows[i + 1][0]))
    connections.sort(key=lambda c: c[0])
    db.close()
    return connections, trip_meta, trip_stops


def _nearby_stops(feed_id: str, lat: float, lon: float, max_m: float) -> list[tuple[str, int]]:
    """Stops within walking distance of a coord, as (stop_id, walk_sec)."""
    out = []
    for sid, (_, slat, slon) in _stops(feed_id).items():
        d = _haversine(lat, lon, slat, slon)
        if d <= max_m:
            out.append((sid, int(d / WALK_SPEED)))
    out.sort(key=lambda x: x[1])
    return out[:60]


def plan(feed_id: str, from_lat: float, from_lon: float,
         to_lat: float, to_lon: float, depart_at: dt.datetime,
         delays: dict[str, int] | None = None) -> list[dict]:
    """One earliest-arrival itinerary (with transfers) from origin to dest.
    Returns [] when unreachable.

    `delays` (trip_id -> seconds) are applied to every connection's
    departure/arrival BEFORE the scan, so the router itself decides with live
    times: a transfer that a delay makes impossible is rejected, and a
    delayed-but-now-faster alternative wins on merit."""
    delays = delays or {}
    stops = _stops(feed_id)
    starts = _nearby_stops(feed_id, from_lat, from_lon, MAX_ORIGIN_WALK)
    ends = dict(_nearby_stops(feed_id, to_lat, to_lon, MAX_ORIGIN_WALK))
    if not starts or not ends:
        return []

    connections, trip_meta, trip_stops = _day_connections(feed_id, depart_at.strftime("%Y%m%d"))
    if not connections:
        return []
    if delays:
        # Shift each delayed trip's connections and restore the scan order
        # (CSA requires connections sorted by departure time).
        connections = sorted(
            ((dep + delays.get(tid, 0), arr + delays.get(tid, 0),
              fs, ts, tid, dseq, aseq)
             for dep, arr, fs, ts, tid, dseq, aseq in connections),
            key=lambda c: c[0])
    footpaths = _footpaths(feed_id)
    dep_sec = depart_at.hour * 3600 + depart_at.minute * 60 + depart_at.second

    arrival: dict[str, int] = {}
    pointer: dict[str, tuple] = {}        # stop -> ('ride', conn) | ('walk', from_stop, wsec)
    enter: dict[str, int] = {}            # trip_id -> boarding connection index

    for sid, wsec in starts:
        arrival[sid] = dep_sec + wsec
        pointer[sid] = ("origin", wsec)

    best_end_arrival = INF
    for c_idx, (c_dep, c_arr, c_from, c_to, c_trip, c_dseq, c_aseq) in enumerate(connections):
        if c_dep < dep_sec:
            continue
        if c_dep > best_end_arrival:      # nothing later can improve the target
            break
        boarded = c_trip in enter
        if not boarded and arrival.get(c_from, INF) <= c_dep:
            enter[c_trip] = c_idx
            boarded = True
        if not boarded:
            continue
        if c_arr < arrival.get(c_to, INF):
            arrival[c_to] = c_arr
            pointer[c_to] = ("ride", c_idx)
            if c_to in ends:
                best_end_arrival = min(best_end_arrival, c_arr + ends[c_to])
            for nb, wsec in footpaths.get(c_to, ()):
                t = c_arr + wsec
                if t < arrival.get(nb, INF):
                    arrival[nb] = t
                    pointer[nb] = ("walk", c_to, wsec)
                    if nb in ends:
                        best_end_arrival = min(best_end_arrival, t + ends[nb])

    # Pick the end stop giving the earliest door arrival.
    best_stop, best_total = None, INF
    for sid, wsec in ends.items():
        if sid in arrival and arrival[sid] + wsec < best_total:
            best_total, best_stop = arrival[sid] + wsec, sid
    if best_stop is None:
        return []

    itin = _reconstruct(connections, trip_meta, trip_stops, stops, pointer, enter,
                        best_stop, ends[best_stop], depart_at, dep_sec, delays,
                        (to_lat, to_lon))
    return [itin] if itin else []


def _reconstruct(connections, trip_meta, trip_stops, stops, pointer, enter,
                 end_stop, end_walk, depart_at, dep_sec, delays, dest) -> dict | None:
    legs: list[dict] = []
    cur = end_stop
    guard = 0
    while cur in pointer and pointer[cur][0] != "origin" and guard < 200:
        guard += 1
        kind = pointer[cur]
        if kind[0] == "walk":
            _, from_stop, wsec = kind
            legs.append(_walk_leg(stops, from_stop, cur, wsec))
            cur = from_stop
        else:  # ride
            c_idx = kind[1]
            trip = connections[c_idx][4]
            e_idx = enter[trip]
            board_stop = connections[e_idx][2]
            legs.append(_ride_leg(connections, trip_meta, trip_stops, stops, e_idx, c_idx, delays))
            cur = board_stop
    # Leading origin walk to the first boarded stop.
    ow = pointer.get(cur)
    if ow and ow[0] == "origin":
        legs.append(_walk_leg(stops, None, cur, ow[1], origin=True))
    legs.reverse()

    # Trailing walk from last alight stop to destination.
    if end_walk > 0:
        name, lat, lon = stops[end_stop]
        legs.append({"type": "walk", "from": name, "from_lat": lat, "from_lon": lon,
                     "to": "Destination", "to_lat": dest[0], "to_lon": dest[1],
                     "seconds": end_walk})

    if not legs:
        return None
    start_sec, end_sec = _timestamp_legs(legs, depart_at, dep_sec)
    rides = [l for l in legs if l["type"] == "ride"]
    return {
        "depart": legs[0].get("depart_at"),
        "arrive": legs[-1].get("arrive_at"),
        "duration_min": round((end_sec - start_sec) / 60),
        "transfers": max(0, len(rides) - 1),
        "walk_min": round(sum(l["seconds"] for l in legs if l["type"] == "walk") / 60),
        "live": any(l.get("live") for l in rides),
        "legs": legs,
    }


def _walk_leg(stops, from_stop, to_stop, wsec, origin=False):
    tn, tlat, tlon = stops[to_stop]
    leg = {"type": "walk", "to": tn, "to_lat": tlat, "to_lon": tlon, "seconds": wsec}
    if origin or from_stop is None:
        leg.update({"from": "Origin", "from_lat": None, "from_lon": None})
    else:
        fn, flat, flon = stops[from_stop]
        leg.update({"from": fn, "from_lat": flat, "from_lon": flon})
    return leg


def _ride_leg(connections, trip_meta, trip_stops, stops, e_idx, c_idx, delays):
    trip = connections[e_idx][4]
    meta = trip_meta.get(trip, {})
    board_dep = connections[e_idx][0]
    alight_arr = connections[c_idx][1]
    board_seq = connections[e_idx][5]
    alight_seq = connections[c_idx][6]
    delay = delays.get(trip, 0)
    # This trip's own stops between board and alight (inclusive), in order.
    seq_stops = [sid for seq, sid in trip_stops.get(trip, []) if board_seq <= seq <= alight_seq]
    stop_list = [{"name": stops[s][0], "lat": stops[s][1], "lon": stops[s][2]}
                 for s in seq_stops if s in stops]
    bn, blat, blon = stops[connections[e_idx][2]]
    an, alat, alon = stops[connections[c_idx][3]]
    return {
        "type": "ride",
        "route": meta.get("route"), "mode": meta.get("mode", "bus"),
        "color": meta.get("color"), "headsign": meta.get("headsign", ""),
        "trip_id": trip,
        "board": bn, "board_lat": blat, "board_lon": blon,
        "alight": an, "alight_lat": alat, "alight_lon": alon,
        "board_sec": board_dep, "alight_sec": alight_arr,
        "delay_sec": delay, "live": trip in delays,
        "num_stops": max(1, len(stop_list) - 1),
        "stops": stop_list,
    }


def _timestamp_legs(legs, depart_at, dep_sec) -> tuple[int, int]:
    """Attach wall-clock ISO times. Ride legs use their absolute sec-of-day
    (+delay); walk legs are chained from the previous leg's end. Returns the
    journey's (start_sec, end_sec) so callers can compute a correct duration
    even across midnight."""
    base = depart_at.replace(hour=0, minute=0, second=0, microsecond=0)

    def iso(sec):
        return (base + dt.timedelta(seconds=int(sec))).isoformat(timespec="minutes")

    start_sec = dep_sec
    clock = dep_sec
    first = True
    for leg in legs:
        if leg["type"] == "ride":
            # board/alight times are already live — plan() shifts delayed
            # trips before the scan; delay_sec on the leg is informational.
            leg["depart_at"] = iso(leg["board_sec"])
            leg["arrive_at"] = iso(leg["alight_sec"])
            leg["in_minutes"] = round((leg["board_sec"] - dep_sec) / 60)
            if first:
                start_sec = leg["board_sec"]
            clock = leg["alight_sec"]
        else:
            if first:
                start_sec = clock
            leg["depart_at"] = iso(clock)
            clock += leg["seconds"]
            leg["arrive_at"] = iso(clock)
        first = False
    return start_sec, clock
