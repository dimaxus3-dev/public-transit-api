"""
GTFS Static ingestion — stdlib only, no third-party deps so it runs anywhere.

Downloads a feed's gtfs.zip, parses routes/trips/shapes/stops, dedupes each
route to a canonical shape per direction (the longest variant — GTFS feeds ship
many partial/variant shapes per route), and writes two artifacts per city:

    data/<feed_id>/lines.geojson   FeatureCollection of route geometries (+color)
    data/<feed_id>/stops.json      [{id,name,lat,lon,code}]

These are immutable per feed version and are what the API serves. PostGIS is the
scale-path upgrade (swap store.py); the pipeline stays the same.
"""
from __future__ import annotations
import csv, io, json, os, sys, zipfile, collections, sqlite3, urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODE_BY_ROUTE_TYPE = {
    "0": "tram", "1": "metro", "2": "rail", "3": "bus",
    "4": "ferry", "5": "cable_tram", "6": "aerial", "7": "funicular",
    "11": "trolleybus", "12": "monorail",
}


def _download(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "transit-backend/0.1"})
    with urllib.request.urlopen(req, timeout=90) as r, open(dest, "wb") as f:
        f.write(r.read())


def _rows(z: zipfile.ZipFile, name: str):
    if name not in z.namelist():
        return []
    return list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig")))


def ingest(feed: dict) -> dict:
    """Ingest one feed dict from feeds.json. Returns a summary."""
    fid = feed["id"]
    out = os.path.join(DATA_DIR, fid)
    os.makedirs(out, exist_ok=True)
    zip_path = os.path.join(out, "gtfs.zip")

    url = feed.get("gtfs_static_url", "")
    if not url or url.startswith("unverified"):
        raise SystemExit(f"[{fid}] no verified gtfs_static_url — skipping")
    if os.path.exists(zip_path) and os.environ.get("REUSE_ZIP") == "1":
        print(f"[{fid}] reusing cached {zip_path}")
    else:
        print(f"[{fid}] downloading {url}")
        _download(url, zip_path)

    z = zipfile.ZipFile(zip_path)
    routes = {r["route_id"]: r for r in _rows(z, "routes.txt")}
    trips = _rows(z, "trips.txt")
    stops = _rows(z, "stops.txt")

    # shape_id -> ordered [ [lon,lat], ... ]
    pts = collections.defaultdict(list)
    for s in _rows(z, "shapes.txt"):
        pts[s["shape_id"]].append(
            (int(s["shape_pt_sequence"]), float(s["shape_pt_lon"]), float(s["shape_pt_lat"]))
        )
    shapes = {sid: [[lon, lat] for _, lon, lat in sorted(p)] for sid, p in pts.items()}

    # route_id + direction -> canonical shape (longest variant)
    best = {}  # (route_id, direction) -> (npts, shape_id)
    for t in trips:
        sid = t.get("shape_id")
        if not sid or sid not in shapes:
            continue
        key = (t["route_id"], t.get("direction_id", "0"))
        n = len(shapes[sid])
        if key not in best or n > best[key][0]:
            best[key] = (n, sid)

    features = []
    for (rid, direction), (_, sid) in sorted(best.items()):
        r = routes.get(rid, {})
        rtype = r.get("route_type", "3")
        color = r.get("route_color", "").strip()
        text = r.get("route_text_color", "").strip()
        features.append({
            "type": "Feature",
            "properties": {
                "route_id": rid,
                "short_name": r.get("route_short_name", rid),
                "long_name": r.get("route_long_name", ""),
                "route_type": rtype,
                "mode": MODE_BY_ROUTE_TYPE.get(rtype, "bus"),
                "color": ("#" + color) if color else None,
                "text_color": ("#" + text) if text else None,
                "direction": direction,
            },
            "geometry": {"type": "LineString", "coordinates": shapes[sid]},
        })

    geojson = {"type": "FeatureCollection", "features": features}
    with open(os.path.join(out, "lines.geojson"), "w", encoding="utf-8") as f:
        json.dump(geojson, f)

    stop_list = [{
        "id": s["stop_id"], "code": s.get("stop_code", ""),
        "name": s["stop_name"],
        "lat": float(s["stop_lat"]), "lon": float(s["stop_lon"]),
        "location_type": s.get("location_type", "0"),
        "parent_station": s.get("parent_station", ""),
    } for s in stops if s.get("stop_lat") and s.get("stop_lon")]
    with open(os.path.join(out, "stops.json"), "w", encoding="utf-8") as f:
        json.dump(stop_list, f)

    # Schedule DB (stop_times indexed by stop) powers /departures & "My Stop".
    build_schedule_db(z, os.path.join(out, "gtfs.sqlite"), routes)

    summary = {"feed": fid, "routes": len(routes), "trips": len(trips),
               "shapes": len(shapes), "line_features": len(features), "stops": len(stop_list)}
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[{fid}] {summary}")
    return summary


def _time_to_sec(t: str) -> int | None:
    """GTFS 'HH:MM:SS' → seconds since noon-12h. HH may exceed 24 (after midnight)."""
    try:
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    except Exception:
        return None


def build_schedule_db(z: zipfile.ZipFile, db_path: str, routes: dict) -> None:
    """Compact SQLite for schedule queries: stop_times indexed by stop_id, plus
    trips/routes/calendar so /departures can resolve active services + names."""
    if os.path.exists(db_path):
        os.remove(db_path)
    db = sqlite3.connect(db_path)
    c = db.cursor()
    c.executescript("""
        CREATE TABLE routes(route_id TEXT PRIMARY KEY, short_name TEXT, long_name TEXT, mode TEXT, color TEXT);
        CREATE TABLE trips(trip_id TEXT PRIMARY KEY, route_id TEXT, service_id TEXT, headsign TEXT, direction TEXT);
        CREATE TABLE stop_times(trip_id TEXT, stop_id TEXT, dep_sec INTEGER, seq INTEGER);
        CREATE TABLE calendar(service_id TEXT, mon INT, tue INT, wed INT, thu INT, fri INT, sat INT, sun INT, start_date TEXT, end_date TEXT);
        CREATE TABLE calendar_dates(service_id TEXT, date TEXT, exception_type INT);
        CREATE TABLE stops(stop_id TEXT PRIMARY KEY, name TEXT, lat REAL, lon REAL, parent TEXT);
    """)
    for rid, r in routes.items():
        rtype = r.get("route_type", "3")
        color = r.get("route_color", "").strip()
        # Some agencies (CTA/MBTA rail) leave short_name empty and put "Blue
        # Line" in long_name — fall back so boards never show a blank badge.
        short = r.get("route_short_name", "").strip() or r.get("route_long_name", "").strip() or rid
        c.execute("INSERT OR REPLACE INTO routes VALUES(?,?,?,?,?)",
                  (rid, short, r.get("route_long_name", ""),
                   MODE_BY_ROUTE_TYPE.get(rtype, "bus"), ("#" + color) if color else None))
    c.executemany("INSERT OR REPLACE INTO trips VALUES(?,?,?,?,?)",
                  [(t["trip_id"], t["route_id"], t.get("service_id", ""),
                    t.get("trip_headsign", ""), t.get("direction_id", "0")) for t in _rows(z, "trips.txt")])
    st_rows = []
    for st in _rows(z, "stop_times.txt"):
        sec = _time_to_sec(st.get("departure_time") or st.get("arrival_time") or "")
        if sec is None:
            continue
        st_rows.append((st["trip_id"], st["stop_id"], sec, int(st.get("stop_sequence", 0))))
    c.executemany("INSERT INTO stop_times VALUES(?,?,?,?)", st_rows)
    c.executemany("INSERT INTO calendar VALUES(?,?,?,?,?,?,?,?,?,?)",
                  [(r["service_id"], int(r["monday"]), int(r["tuesday"]), int(r["wednesday"]),
                    int(r["thursday"]), int(r["friday"]), int(r["saturday"]), int(r["sunday"]),
                    r["start_date"], r["end_date"]) for r in _rows(z, "calendar.txt")])
    c.executemany("INSERT INTO calendar_dates VALUES(?,?,?)",
                  [(r["service_id"], r["date"], int(r["exception_type"])) for r in _rows(z, "calendar_dates.txt")])
    c.executemany("INSERT OR REPLACE INTO stops VALUES(?,?,?,?,?)",
                  [(s["stop_id"], s["stop_name"], float(s["stop_lat"]), float(s["stop_lon"]),
                    s.get("parent_station", ""))
                   for s in _rows(z, "stops.txt") if s.get("stop_lat") and s.get("stop_lon")])
    c.execute("CREATE INDEX idx_st_stop ON stop_times(stop_id, dep_sec)")
    c.execute("CREATE INDEX idx_cd ON calendar_dates(date, service_id)")
    c.execute("CREATE INDEX idx_stop_parent ON stops(parent)")
    db.commit()
    db.close()


if __name__ == "__main__":
    reg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "feeds.json")))
    want = sys.argv[1] if len(sys.argv) > 1 else "szczecin-zditm"
    feed = next((f for f in reg["feeds"] if f["id"] == want), None)
    if not feed:
        raise SystemExit(f"feed '{want}' not found in feeds.json")
    ingest(feed)
