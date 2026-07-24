"""End-to-end API tests over a tiny synthetic GTFS feed.

Builds a 3-stop tram feed as a real GTFS zip, ingests it through the actual
ingest pipeline (via a file:// URL), then exercises the HTTP API with
fastapi's TestClient. No network, no external data.
"""
import io
import json
import os
import shutil
import zipfile

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.join(os.path.dirname(__file__), "..")
FID = "test-fixture"
DATA_DIR = os.path.join(ROOT, "data", FID)

# Three stops along one street in a made-up city.
STOPS = [("A", "Alpha", 50.0000, 20.0000),
         ("B", "Bravo", 50.0050, 20.0050),
         ("C", "Charlie", 50.0100, 20.0100)]


def _gtfs_zip() -> bytes:
    def csv(*lines):
        return "\n".join(lines) + "\n"

    files = {
        "agency.txt": csv("agency_id,agency_name,agency_url,agency_timezone",
                          "ag,Test Agency,https://example.com,Europe/Warsaw"),
        "routes.txt": csv("route_id,route_short_name,route_long_name,route_type,route_color",
                          "T1,1,Alpha - Charlie,0,005E85"),
        "stops.txt": csv("stop_id,stop_name,stop_lat,stop_lon",
                         *[f"{sid},{name},{lat},{lon}" for sid, name, lat, lon in STOPS]),
        "shapes.txt": csv("shape_id,shape_pt_sequence,shape_pt_lat,shape_pt_lon",
                          *[f"s1,{i},{lat},{lon}" for i, (_, _, lat, lon) in enumerate(STOPS)]),
        "calendar.txt": csv("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date",
                            "daily,1,1,1,1,1,1,1,20200101,20351231"),
        "calendar_dates.txt": csv("service_id,date,exception_type"),
    }
    # A tram every 30 minutes, 05:00–23:30, A -> B -> C (5 min per hop).
    trips = ["route_id,service_id,trip_id,trip_headsign,direction_id,shape_id"]
    stop_times = ["trip_id,stop_id,arrival_time,departure_time,stop_sequence"]
    for i, minutes in enumerate(range(5 * 60, 23 * 60 + 31, 30)):
        tid = f"t{i}"
        trips.append(f"T1,daily,{tid},Charlie,0,s1")
        for seq, (sid, *_rest) in enumerate(STOPS):
            t = minutes + seq * 5
            hhmm = f"{t // 60:02d}:{t % 60:02d}:00"
            stop_times.append(f"{tid},{sid},{hhmm},{hhmm},{seq}")
    files["trips.txt"] = "\n".join(trips) + "\n"
    files["stop_times.txt"] = "\n".join(stop_times) + "\n"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


@pytest.fixture(scope="session", autouse=True)
def ingested_fixture(tmp_path_factory):
    zip_path = tmp_path_factory.mktemp("gtfs") / "fixture.zip"
    zip_path.write_bytes(_gtfs_zip())
    from app import ingest
    summary = ingest.ingest({"id": FID, "gtfs_static_url": zip_path.as_uri()})
    assert summary["routes"] == 1 and summary["stops"] == 3
    yield
    shutil.rmtree(DATA_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def client():
    from app.main import app
    return TestClient(app)


def test_health_lists_fixture(client):
    data = client.get("/health").json()
    assert data["ok"] is True
    assert FID in data["ingested_feeds"]
    assert data["registered_feeds"] > 1000        # world catalog is loaded


def test_feeds_browse_and_filters(client):
    all_ = client.get("/feeds", params={"limit": 2000}).json()
    assert all_["total"] > 1000
    it = client.get("/feeds", params={"country": "IT"}).json()
    assert it["total"] > 0
    assert all(f["country"] == "IT" for f in it["feeds"])
    named = client.get("/feeds", params={"q": "venice"}).json()
    assert any("venice" in (f["city"] or "").lower() for f in named["feeds"])


def test_countries_summary(client):
    per = client.get("/countries").json()
    assert per.get("US", 0) > 100


def test_routes_and_geometry(client):
    routes = client.get("/routes", params={"city": FID}).json()
    assert [r["route_id"] for r in routes] == ["T1"]
    assert routes[0]["mode"] == "tram"
    geo = client.get(f"/routes/{FID}/T1/geometry").json()
    assert geo["features"][0]["geometry"]["coordinates"] == [
        [lon, lat] for _, _, lat, lon in STOPS]


def test_stops_nearby(client):
    near = client.get("/stops/nearby", params={
        "city": FID, "lat": 50.0001, "lng": 20.0001, "radius": 300}).json()
    assert [s["name"] for s in near] == ["Alpha"]


def test_departures_board(client):
    deps = client.get(f"/stops/{FID}/A/departures",
                      params={"limit": 3}).json()
    assert deps["stop_name"] == "Alpha"
    assert len(deps["departures"]) > 0
    assert all(d["route"] == "1" for d in deps["departures"])


def test_journey_plans_a_to_c(client):
    plan = client.get("/journey", params={
        "city": FID, "from_lat": 50.0, "from_lon": 20.0,
        "to_lat": 50.01, "to_lon": 20.01,
        "time": "2030-06-03T09:00:00"}).json()
    assert plan["itineraries"], "no itinerary found"
    it = plan["itineraries"][0]
    rides = [l for l in it["legs"] if l["type"] == "ride"]
    assert rides and rides[0]["route"] == "1"
    assert rides[0]["board"] == "Alpha" and rides[0]["alight"] == "Charlie"
    assert it["transfers"] == 0


def test_ingest_endpoint_locked_down_by_default(client, monkeypatch):
    import app.main as m
    monkeypatch.setitem(m._FEEDS, FID, {"id": FID})
    # No ADMIN_KEY on the server -> ingest is disabled entirely.
    assert client.post(f"/feeds/{FID}/ingest").status_code == 403
    # Key set -> requires the right X-API-Key.
    monkeypatch.setattr(m, "_ADMIN_KEY", "sekret")
    assert client.post(f"/feeds/{FID}/ingest").status_code == 401
    assert client.post(f"/feeds/{FID}/ingest",
                       headers={"X-API-Key": "wrong"}).status_code == 401
    hdr = {"X-API-Key": "sekret"}
    r = client.post("/feeds/definitely-not-a-feed/ingest", headers=hdr)
    assert r.status_code == 404
    r = client.post(f"/feeds/{FID}/ingest", headers=hdr)
    assert r.json()["status"] == "already ingested"
    # Concurrency cap: with 2 ingests already running, a third is rejected
    # (force=true skips the already-ingested short-circuit).
    monkeypatch.setattr(m, "_ingesting", {"a", "b"})
    r = client.post("/feeds/mdb-1063/ingest", headers=hdr,
                    params={"force": "true"})
    assert r.status_code == 429


def test_rate_limit_kicks_in(client, monkeypatch):
    import app.main as m
    monkeypatch.setattr(m, "_RATE", 3)
    m._hits.clear()
    codes = [client.get("/health").status_code for _ in range(5)]
    assert 429 in codes
    monkeypatch.setattr(m, "_RATE", 120)
    m._hits.clear()


def test_errors_are_rfc7807(client):
    r = client.get("/routes", params={"city": "no-such-city"})
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["status"] == 404 and "title" in body and "detail" in body
    v = client.get("/journey", params={"city": FID})       # missing lat/lon
    assert v.status_code == 422
    assert v.headers["content-type"].startswith("application/problem+json")


def test_metrics_exposition(client):
    client.get("/health")
    m = client.get("/metrics")
    assert m.status_code == 200
    text = m.text
    assert "transit_requests_total" in text
    assert 'path="/health"' in text
    assert "transit_ingested_feeds" in text


def test_vehicles_stream_rejects_feed_without_rt(client):
    r = client.get("/vehicles/stream", params={"city": FID})
    assert r.status_code == 404
    assert r.json()["title"] == "Not Found"


def test_python_sdk_against_test_app(client, monkeypatch):
    import sys, os
    sys.path.insert(0, os.path.join(ROOT, "clients", "python"))
    import transit_client as tc

    def fake_call(self, method, path, **params):
        clean = {k: v for k, v in params.items() if v is not None}
        fn = client.get if method == "GET" else client.post
        r = fn(path, params=clean)
        if r.status_code >= 400:
            raise tc.TransitError(r.status_code, r.json())
        return r.json()

    monkeypatch.setattr(tc.TransitClient, "_call", fake_call)
    t = tc.TransitClient()
    assert FID in t.health()["ingested_feeds"]
    assert t.routes(FID)[0]["route_id"] == "T1"
    plan = t.journey(FID, 50.0, 20.0, 50.01, 20.01, time="2030-06-03T09:00:00")
    assert plan["itineraries"]
    with pytest.raises(tc.TransitError) as e:
        t.routes("nope-city")
    assert e.value.status == 404


def test_delays_degrade_to_static_schedule(client, monkeypatch):
    """RT stream down → departures still 200 from the static timetable,
    upstream tried exactly once per backoff window (no per-request hangs)."""
    import app.main as m
    from app import realtime

    attempts = {"n": 0}

    def dead_urlopen(*a, **kw):
        attempts["n"] += 1
        raise OSError("connection reset")

    monkeypatch.setitem(m._FEEDS, FID,
                        {"id": FID, "gtfs_rt_trips_url": "http://rt.example/pb"})
    monkeypatch.setattr(realtime.urllib.request, "urlopen", dead_urlopen)
    realtime._DELAY_CACHE.pop(FID, None)
    realtime._delay_fail_at.pop(FID, None)

    for _ in range(3):
        r = client.get(f"/stops/{FID}/A/departures", params={"limit": 3})
        assert r.status_code == 200
        assert all(not d["live"] and d["delay_sec"] == 0
                   for d in r.json()["departures"])
    assert attempts["n"] == 1          # backoff: one probe, not one per request

    realtime._delay_fail_at.pop(FID, None)


def test_vehicles_serve_stale_frame_when_upstream_dies(monkeypatch):
    from app import realtime
    import time as _t

    realtime._CACHE["ghost"] = (_t.time() - 10, [{"id": "v1"}])   # stale but recent
    realtime._fail_at.pop("ghost", None)

    def dead_urlopen(*a, **kw):
        raise OSError("timed out")

    monkeypatch.setattr(realtime.urllib.request, "urlopen", dead_urlopen)
    assert realtime.vehicles_live("ghost", "http://rt.example/pb") == [{"id": "v1"}]

    realtime._CACHE["ghost"] = (_t.time() - 300, [{"id": "v1"}])  # too old to trust
    realtime._fail_at.pop("ghost", None)
    with pytest.raises(Exception):
        realtime.vehicles_live("ghost", "http://rt.example/pb")
    with pytest.raises(RuntimeError, match="backoff"):            # instant, no fetch
        realtime.vehicles_live("ghost", "http://rt.example/pb")

    realtime._CACHE.pop("ghost", None)
    realtime._fail_at.pop("ghost", None)


def test_prewarm_builds_ram_caches(client):
    import app.main as m
    from app import routing
    routing._stops.cache_clear()
    routing._day_connections.cache_clear()
    assert m._prewarm_feeds() >= 1                     # fixture feed warmed
    assert routing._stops.cache_info().currsize >= 1
    assert routing._day_connections.cache_info().currsize >= 1


# ── ingest hardening ─────────────────────────────────────────────────────────

def _zip_of(files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


def test_ingest_rejects_corrupted_and_hostile_zips(tmp_path):
    from app import ingest

    bad = tmp_path / "corrupt.zip"
    bad.write_bytes(b"this is not a zip at all")
    with pytest.raises(Exception):
        ingest.ingest({"id": "evil-1", "gtfs_static_url": bad.as_uri()})

    traversal = tmp_path / "traversal.zip"
    traversal.write_bytes(_zip_of({"../../escape.txt": "boom",
                                   "routes.txt": "route_id\nX"}))
    with pytest.raises(ValueError, match="suspicious zip entry"):
        ingest.ingest({"id": "evil-2", "gtfs_static_url": traversal.as_uri()})

    not_gtfs = tmp_path / "notgtfs.zip"
    not_gtfs.write_bytes(_zip_of({"readme.txt": "hello"}))
    with pytest.raises(ValueError, match="missing routes.txt"):
        ingest.ingest({"id": "evil-3", "gtfs_static_url": not_gtfs.as_uri()})

    # nothing half-written left behind for any of them
    for fid in ("evil-1", "evil-2", "evil-3"):
        assert not os.path.exists(os.path.join(ROOT, "data", fid))
        assert not os.path.exists(os.path.join(ROOT, "data", f".build-{fid}"))


def test_ingest_download_size_cap(tmp_path, monkeypatch):
    from app import ingest
    monkeypatch.setattr(ingest, "MAX_ZIP_MB", 0)      # cap = 0 bytes
    z = tmp_path / "any.zip"
    z.write_bytes(_zip_of({"routes.txt": "route_id\nX"}))
    with pytest.raises(ValueError, match="exceeds 0 MB"):
        ingest.ingest({"id": "evil-4", "gtfs_static_url": z.as_uri()})
    assert not os.path.exists(os.path.join(ROOT, "data", ".build-evil-4"))


def test_reingest_is_atomic_and_busts_caches(client, tmp_path):
    """Re-ingesting a live feed replaces it atomically and the running API
    serves the NEW data immediately (caches invalidated)."""
    import app.main as m
    from app import ingest

    assert client.get("/routes", params={"city": FID}).json()[0]["route_id"] == "T1"

    # v2 of the fixture: same city, route renamed to T2.
    v2 = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n"
                      "ag,T,https://x,Europe/Warsaw\n",
        "routes.txt": "route_id,route_short_name,route_type\nT2,2,0\n",
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\n"
                     + "".join(f"{sid},{name},{lat},{lon}\n" for sid, name, lat, lon in STOPS),
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,"
                        "saturday,sunday,start_date,end_date\n"
                        "daily,1,1,1,1,1,1,1,20200101,20351231\n",
        "trips.txt": "route_id,service_id,trip_id,direction_id,shape_id\nT2,daily,t0,0,s1\n",
        "stop_times.txt": "trip_id,stop_id,departure_time,stop_sequence\n"
                          "t0,A,09:00:00,0\nt0,B,09:05:00,1\nt0,C,09:10:00,2\n",
        "shapes.txt": "shape_id,shape_pt_sequence,shape_pt_lat,shape_pt_lon\n"
                      + "".join(f"s1,{i},{lat},{lon}\n"
                                for i, (_, _, lat, lon) in enumerate(STOPS)),
    }
    p = tmp_path / "v2.zip"
    p.write_bytes(_zip_of(v2))
    ingest.ingest({"id": FID, "gtfs_static_url": p.as_uri()})
    m._invalidate_caches()

    routes = client.get("/routes", params={"city": FID}).json()
    assert [r["route_id"] for r in routes] == ["T2"]
    assert client.get("/health").json()  # feed still healthy after swap

    # restore v1 for any later tests
    p1 = tmp_path / "v1.zip"
    p1.write_bytes(_gtfs_zip())
    ingest.ingest({"id": FID, "gtfs_static_url": p1.as_uri()})
    m._invalidate_caches()


def test_world_feed_timezone_captured_at_ingest():
    summary = json.load(open(os.path.join(ROOT, "data", FID, "summary.json")))
    assert summary["timezone"] == "Europe/Warsaw"
    import app.main as m
    assert m._feed_timezone(FID) == "Europe/Warsaw"


# ── routing correctness with live delays ─────────────────────────────────────

TRANSFER_FID = "test-transfer"


@pytest.fixture(scope="session")
def transfer_feed(tmp_path_factory):
    """Two routes meeting at B: R1 A->B arrives 09:00; R2 departs B at 09:10
    and at 10:10. A 15-min delay on R1 must push the plan onto the 10:10.
    Stops are ~3.3 km apart so walking can never beat the ride."""
    stops_csv = "stop_id,stop_name,stop_lat,stop_lon\n" \
                "A,Alpha,50.0,20.0\nB,Bravo,50.03,20.0\nC,Charlie,50.06,20.0\n"
    files = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n"
                      "ag,T,https://x,Europe/Warsaw\n",
        "routes.txt": "route_id,route_short_name,route_type\nR1,1,3\nR2,2,3\n",
        "stops.txt": stops_csv,
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,"
                        "saturday,sunday,start_date,end_date\n"
                        "daily,1,1,1,1,1,1,1,20200101,20351231\n",
        "trips.txt": "route_id,service_id,trip_id,direction_id\n"
                     "R1,daily,r1,0\nR2,daily,r2a,0\nR2,daily,r2b,0\n",
        "stop_times.txt": "trip_id,stop_id,departure_time,stop_sequence\n"
                          "r1,A,08:40:00,0\nr1,B,09:00:00,1\n"
                          "r2a,B,09:10:00,0\nr2a,C,09:30:00,1\n"
                          "r2b,B,10:10:00,0\nr2b,C,10:30:00,1\n",
    }
    p = tmp_path_factory.mktemp("gtfs2") / "transfer.zip"
    p.write_bytes(_zip_of(files))
    from app import ingest
    ingest.ingest({"id": TRANSFER_FID, "gtfs_static_url": p.as_uri()})
    yield
    shutil.rmtree(os.path.join(ROOT, "data", TRANSFER_FID), ignore_errors=True)


def test_delay_reroutes_impossible_transfer(transfer_feed):
    import datetime as dt
    from app import routing
    routing._day_connections.cache_clear()
    when = dt.datetime(2030, 6, 3, 8, 30)

    static = routing.plan(TRANSFER_FID, 50.0, 20.0, 50.06, 20.0, when)[0]
    assert static["arrive"].endswith("09:30")          # catches the 09:10

    live = routing.plan(TRANSFER_FID, 50.0, 20.0, 50.06, 20.0, when,
                        delays={"r1": 900})[0]         # R1 +15 min -> B at 09:15
    assert live["arrive"].endswith("10:30")            # 09:10 now impossible
    rides = [l for l in live["legs"] if l["type"] == "ride"]
    assert rides[0]["delay_sec"] == 900 and rides[0]["live"]


def test_departures_after_midnight_gtfs_times(transfer_feed, tmp_path):
    """GTFS 24:xx/25:xx times must appear on late-night boards (day_offset)."""
    from app import ingest, schedule
    import datetime as dt
    files_late = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n"
                      "ag,T,https://x,Europe/Warsaw\n",
        "routes.txt": "route_id,route_short_name,route_type\nN1,N1,3\n",
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nA,Alpha,50.0,20.0\nB,Bravo,50.005,20.005\n",
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,"
                        "saturday,sunday,start_date,end_date\n"
                        "daily,1,1,1,1,1,1,1,20200101,20351231\n",
        "trips.txt": "route_id,service_id,trip_id,direction_id\nN1,daily,n1,0\n",
        "stop_times.txt": "trip_id,stop_id,departure_time,stop_sequence\n"
                          "n1,A,24:15:00,0\nn1,B,25:05:00,1\n",
    }
    p = tmp_path / "night.zip"
    p.write_bytes(_zip_of(files_late))
    fid = "test-night"
    ingest.ingest({"id": fid, "gtfs_static_url": p.as_uri()})
    try:
        board = schedule.departures(fid, "A", at=dt.datetime(2030, 6, 3, 23, 50))
        deps = board["departures"]
        # 24:15 of June 3rd's service day = 00:15 on the clock, 25 min away —
        # still day_offset 0 (it belongs to TODAY's service day).
        assert ("00:15", 0) in [(d["time"], d["day_offset"]) for d in deps]
        night = next(d for d in deps if d["time"] == "00:15" and d["day_offset"] == 0)
        assert night["in_minutes"] == 25
    finally:
        shutil.rmtree(os.path.join(ROOT, "data", fid), ignore_errors=True)
