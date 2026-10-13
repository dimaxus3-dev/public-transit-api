"""Bounded, read-only schedule samples for the map's day replay.

The endpoint deliberately serves a deterministic sample of active trips rather
than streaming an entire national GTFS timetable to each browser.
"""

from __future__ import annotations

import datetime as dt
import functools
import hashlib
import os
import sqlite3
from collections import defaultdict

from . import paths, store

MAX_TRIPS = 800
MODES = frozenset({"metro", "rail", "tram", "bus", "trolleybus", "ferry"})
WEEKDAY = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def replay(city: str, day: dt.date, mode: str) -> dict:
    """Return a fixed-size sample of scheduled vehicle traces for one day."""
    if city not in store.available_feeds():
        raise ValueError("city is not ingested")
    if mode not in MODES:
        raise ValueError("unsupported mode")
    path = os.path.join(paths.DATA_DIR, city, "gtfs.sqlite")
    return _cached(city, day.isoformat(), mode, os.path.getmtime(path))


@functools.lru_cache(maxsize=16)
def _cached(city: str, day: str, mode: str, _mtime: float) -> dict:
    path = os.path.join(paths.DATA_DIR, city, "gtfs.sqlite")
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        stamp = day.replace("-", "")
        weekday = WEEKDAY[dt.date.fromisoformat(day).weekday()]
        services = {
            row[0]
            for row in db.execute(
                f"SELECT service_id FROM calendar WHERE {weekday}=1 "
                "AND start_date<=? AND end_date>=?",
                (stamp, stamp),
            )
        }
        for sid, action in db.execute(
            "SELECT service_id, exception_type FROM calendar_dates WHERE date=?", (stamp,)
        ):
            if action == 1:
                services.add(sid)
            elif action == 2:
                services.discard(sid)
        if not services:
            return {"city": city, "date": day, "mode": mode, "sampled": False, "active_trips": 0, "trips": []}

        placeholders = ",".join("?" for _ in services)
        groups: dict[str, list[tuple]] = defaultdict(list)
        for trip_id, route_id, short, color in db.execute(
            "SELECT t.trip_id,t.route_id,r.short_name,r.color FROM trips t "
            "JOIN routes r ON r.route_id=t.route_id "
            f"WHERE r.mode=? AND t.service_id IN ({placeholders})",
            (mode, *sorted(services)),
        ):
            groups[route_id].append((trip_id, short, color))
        active_trips = sum(map(len, groups.values()))
        if not groups:
            return {"city": city, "date": day, "mode": mode, "sampled": False, "active_trips": 0, "trips": []}

        # Stable per-route sampling prevents a long route from hiding every
        # other line. Hash order avoids depending on provider-specific trip IDs.
        quota = max(1, MAX_TRIPS // len(groups))
        chosen = {}
        for route_id in sorted(groups):
            ordered = sorted(groups[route_id], key=lambda item: hashlib.blake2s(item[0].encode(), digest_size=8).digest())
            for trip_id, short, color in ordered[:quota]:
                chosen[trip_id] = (short, color)
        if len(chosen) > MAX_TRIPS:
            chosen = dict(list(chosen.items())[:MAX_TRIPS])

        stop_coords = {
            sid: (lon, lat)
            for sid, lat, lon in db.execute("SELECT stop_id,lat,lon FROM stops")
            if lat is not None and lon is not None
        }
        points: dict[str, list[list]] = defaultdict(list)
        ids = list(chosen)
        # One bounded SQL table scan. There is no trip_id index in the existing
        # artifacts; issuing one query per chosen trip would rescan millions of rows.
        for offset in range(0, len(ids), 800):
            batch = ids[offset : offset + 800]
            ph = ",".join("?" for _ in batch)
            for trip_id, stop_id, arrival, departure, seq in db.execute(
                f"SELECT trip_id,stop_id,arrival_sec,departure_sec,stop_sequence "
                f"FROM stop_times WHERE trip_id IN ({ph})",
                batch,
            ):
                coord = stop_coords.get(stop_id)
                sec = departure if departure is not None else arrival
                if coord and sec is not None:
                    points[trip_id].append([seq, int(sec), round(coord[0], 6), round(coord[1], 6)])
        trips = []
        for trip_id in ids:
            trace = sorted(points.get(trip_id, []))
            if len(trace) < 2:
                continue
            short, color = chosen[trip_id]
            trips.append({"id": trip_id, "route": short, "color": color, "points": [p[1:] for p in trace]})
        return {"city": city, "date": day, "mode": mode, "sampled": len(chosen) < active_trips, "active_trips": active_trips, "trips": trips}
    finally:
        db.close()
