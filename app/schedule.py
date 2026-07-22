"""
Schedule queries over the per-feed SQLite built by ingest — powers /departures
and the iOS "My Stop" board. Resolves GTFS calendar + calendar_dates to the
services running on a given date, then the next departures at a stop.
"""
from __future__ import annotations
import datetime as dt
import os
import sqlite3

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_WEEKDAY_COL = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # Python Mon=0


def _db(feed_id: str) -> sqlite3.Connection | None:
    path = os.path.join(DATA_DIR, feed_id, "gtfs.sqlite")
    return sqlite3.connect(path) if os.path.exists(path) else None


def _active_services(db: sqlite3.Connection, day: dt.date) -> set[str]:
    date = day.strftime("%Y%m%d")
    col = _WEEKDAY_COL[day.weekday()]
    svc = {r[0] for r in db.execute(
        f"SELECT service_id FROM calendar WHERE {col}=1 AND start_date<=? AND end_date>=?",
        (date, date))}
    for sid, etype in db.execute(
            "SELECT service_id, exception_type FROM calendar_dates WHERE date=?", (date,)):
        if etype == 1:
            svc.add(sid)
        elif etype == 2:
            svc.discard(sid)
    return svc


def _expand_stop_ids(db: sqlite3.Connection, stop_id: str) -> list[str]:
    """A station (parent) has no stop_times of its own — expand to its child
    platform stops. A plain stop expands to just itself."""
    ids = [stop_id]
    try:
        ids += [r[0] for r in db.execute("SELECT stop_id FROM stops WHERE parent=?", (stop_id,))]
    except sqlite3.OperationalError:
        pass  # older DB without the parent column
    return ids


def stop_name(feed_id: str, stop_id: str) -> str | None:
    db = _db(feed_id)
    if not db:
        return None
    row = db.execute("SELECT name FROM stops WHERE stop_id=?", (stop_id,)).fetchone()
    return row[0] if row else None


def search_stops(feed_id: str, query: str, limit: int = 12) -> list[dict]:
    db = _db(feed_id)
    if not db:
        return []
    q = f"%{query.strip().lower()}%"
    try:
        rows = db.execute("""
            SELECT stop_id, name, lat, lon FROM stops
            WHERE lower(name) LIKE ?
            ORDER BY (parent='' OR parent IS NULL) DESC, name LIMIT ?
        """, (q, limit * 4))
    except sqlite3.OperationalError:
        rows = db.execute(
            "SELECT stop_id, name, lat, lon FROM stops WHERE lower(name) LIKE ? ORDER BY name LIMIT ?",
            (q, limit))
    seen, out = set(), []
    for r in rows:
        if r[1] in seen:
            continue
        seen.add(r[1])
        out.append({"id": r[0], "name": r[1], "lat": r[2], "lon": r[3]})
        if len(out) >= limit:
            break
    return out


def directions(feed_id: str, stop_id: str) -> list[dict]:
    """Distinct directions served at a stop, each with a sample headsign — so the
    UI can offer a 'both directions' selector."""
    db = _db(feed_id)
    if not db:
        return []
    sids = _expand_stop_ids(db, stop_id)
    ph = ",".join("?" * len(sids))
    rows = db.execute(f"""
        SELECT t.direction, t.headsign, COUNT(*) n
        FROM stop_times st JOIN trips t ON st.trip_id = t.trip_id
        WHERE st.stop_id IN ({ph})
        GROUP BY t.direction, t.headsign
        ORDER BY t.direction, n DESC
    """, sids)
    seen, out = set(), []
    for direction, headsign, _ in rows:
        if direction in seen:
            continue
        seen.add(direction)
        out.append({"direction": direction, "headsign": headsign})
    return out


def departures(feed_id: str, stop_id: str, at: dt.datetime | None = None,
               limit: int = 15, direction: str | None = None,
               delays: dict[str, int] | None = None) -> dict:
    db = _db(feed_id)
    if not db:
        return {"stop_id": stop_id, "departures": [], "error": "feed not ingested"}
    delays = delays or {}
    at = at or dt.datetime.now()
    out: list[dict] = []
    dir_clause = "AND t.direction = ?" if direction is not None else ""
    sids = _expand_stop_ids(db, stop_id)
    sid_ph = ",".join("?" * len(sids))

    for day_offset in (0, 1):
        if len(out) >= limit:
            break
        day = (at + dt.timedelta(days=day_offset)).date()
        svc = _active_services(db, day)
        if not svc:
            continue
        placeholders = ",".join("?" * len(svc))
        now_sec = at.hour * 3600 + at.minute * 60 + at.second
        if day_offset == 0:
            where, bounds = "AND st.dep_sec >= ?", [now_sec]
        else:
            # next-day early departures only (avoid double-counting today's >24h trips)
            where, bounds = "AND st.dep_sec < 86400", []
        dir_bind = [direction] if direction is not None else []
        rows = db.execute(f"""
            SELECT st.dep_sec, r.short_name, t.headsign, r.mode, r.color, t.direction, st.trip_id
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.trip_id
            JOIN routes r ON t.route_id = r.route_id
            WHERE st.stop_id IN ({sid_ph}) AND t.service_id IN ({placeholders}) {where} {dir_clause}
            ORDER BY st.dep_sec
            LIMIT ?
        """, [*sids, *svc, *bounds, *dir_bind, limit - len(out)])
        for dep_sec, short, head, mode, color, direction, trip_id in rows:
            # Live: shift the scheduled time by the trip's realtime delay when
            # today's trip is actually being tracked right now.
            live = day_offset == 0 and trip_id in delays
            delay = delays.get(trip_id, 0) if live else 0
            eff = dep_sec + delay
            hh, mm = (eff // 3600) % 24, (eff // 60) % 60
            eta_min = ((eff - now_sec) // 60) if day_offset == 0 else None
            out.append({
                "route": short, "headsign": head, "mode": mode, "color": color,
                "direction": direction,
                "time": f"{hh:02d}:{mm:02d}",
                "in_minutes": eta_min if (eta_min is not None and eta_min >= 0) else None,
                "day_offset": day_offset,
                "live": live, "delay_sec": delay,
            })

    return {"stop_id": stop_id, "stop_name": stop_name(feed_id, stop_id),
            "generated_at": at.isoformat(timespec="seconds"), "departures": out}


def route_stops(feed_id: str, route_id: str, direction: str = "0") -> list[dict]:
    """Ordered stops for one direction of a route — the calling pattern of its
    longest trip (most stops), which is the canonical variant the map draws."""
    db = _db(feed_id)
    if not db:
        return []
    trip = db.execute("""
        SELECT st.trip_id, COUNT(*) n FROM stop_times st
        JOIN trips t ON t.trip_id = st.trip_id
        WHERE t.route_id = ? AND t.direction = ?
        GROUP BY st.trip_id ORDER BY n DESC LIMIT 1
    """, (route_id, direction)).fetchone()
    if not trip:
        return []
    rows = db.execute("""
        SELECT s.stop_id, s.name, s.lat, s.lon, st.seq
        FROM stop_times st JOIN stops s ON s.stop_id = st.stop_id
        WHERE st.trip_id = ? ORDER BY st.seq
    """, (trip[0],))
    return [{"id": r[0], "name": r[1], "lat": r[2], "lon": r[3], "seq": r[4]} for r in rows]
