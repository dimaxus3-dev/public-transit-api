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


def test_ingest_endpoint_auth_and_validation(client, monkeypatch):
    import app.main as m
    monkeypatch.setitem(m._FEEDS, FID, {"id": FID})
    r = client.post("/feeds/definitely-not-a-feed/ingest")
    assert r.status_code == 404
    r = client.post(f"/feeds/{FID}/ingest")
    assert r.json()["status"] == "already ingested"
    monkeypatch.setattr(m, "_ADMIN_KEY", "sekret")
    assert client.post(f"/feeds/{FID}/ingest").status_code == 401
    ok = client.post(f"/feeds/{FID}/ingest", headers={"X-API-Key": "sekret"})
    assert ok.status_code == 200


def test_rate_limit_kicks_in(client, monkeypatch):
    import app.main as m
    monkeypatch.setattr(m, "_RATE", 3)
    m._hits.clear()
    codes = [client.get("/health").status_code for _ in range(5)]
    assert 429 in codes
    monkeypatch.setattr(m, "_RATE", 120)
    m._hits.clear()
