"""Offline checks for the MapLibre demo shell and its local assets."""

import sqlite3

from fastapi.testclient import TestClient

from app.main import app


def test_demo_shell_and_vendored_assets():
    client = TestClient(app)
    page = client.get("/demo")
    assert page.status_code == 200
    assert "https://tiles.openfreemap.org/styles/dark" not in page.text  # configured in JS
    assert '/static/vendor/maplibre-gl.js' in page.text
    assert '/static/demo.js' in page.text
    assert 'id="city"' in page.text
    script = client.get("/static/demo.js")
    assert script.status_code == 200
    assert "https://tiles.openfreemap.org/styles/dark" in script.text
    assert "/cities" in script.text
    assert "lines.geojson" in script.text
    assert client.get("/static/vendor/maplibre-gl.js").status_code == 200
    assert client.get("/static/vendor/maplibre-gl.css").status_code == 200


def test_demo_does_not_change_feed_route():
    client = TestClient(app)
    assert client.get("/feeds").status_code == 200


def test_stop_board_and_clustering_are_in_demo():
    client = TestClient(app)
    html = client.get("/demo").text
    js = client.get("/static/demo.js").text
    assert 'id="board"' in html
    assert 'id="board-list"' in html
    assert "cluster:true" in js
    assert "stop-clusters" in js
    assert "/departures?limit=7" in js
    assert "encodeURIComponent(id)" in js  # stop IDs may contain colons


def test_journey_map_uses_existing_api_and_reduced_motion():
    client = TestClient(app)
    html = client.get("/demo").text
    js = client.get("/static/demo.js").text
    assert 'id="plan-button"' in html
    assert 'id="journey-card"' in html
    assert "fetch(`/journey?${q}`)" in js
    assert "lineMetrics:true" in js
    assert "line-gradient" in js
    assert "line-dasharray" in js
    assert "prefers-reduced-motion: reduce" in js


def test_live_vehicle_stream_and_interpolation_are_client_only():
    client = TestClient(app)
    js = client.get("/static/demo.js").text
    assert "/map/layers?city=" in js
    assert "new EventSource(`/vehicles/stream?city=" in js
    assert "currentVehicle(v,now)" in js
    assert "text-rotate" in js
    assert "LIVE STALE" in js
    assert "NO LIVE FEED" in js


def test_replay_reads_bounded_day_from_fixture(tmp_path, monkeypatch):
    from app import paths, store

    folder = tmp_path / "sample-city"
    folder.mkdir()
    db = sqlite3.connect(folder / "gtfs.sqlite")
    db.executescript("""
        CREATE TABLE calendar(service_id TEXT,mon INT,tue INT,wed INT,thu INT,fri INT,sat INT,sun INT,start_date TEXT,end_date TEXT);
        CREATE TABLE calendar_dates(service_id TEXT,date TEXT,exception_type INT);
        CREATE TABLE routes(route_id TEXT,short_name TEXT,mode TEXT,color TEXT);
        CREATE TABLE trips(trip_id TEXT,route_id TEXT,service_id TEXT);
        CREATE TABLE stops(stop_id TEXT,lat REAL,lon REAL);
        CREATE TABLE stop_times(trip_id TEXT,stop_id TEXT,arrival_sec INT,departure_sec INT,stop_sequence INT);
        INSERT INTO calendar VALUES('daily',1,1,1,1,1,1,1,'20300101','20301231');
        INSERT INTO routes VALUES('T1','1','tram','#005E85');
        INSERT INTO trips VALUES('trip-a','T1','daily');
        INSERT INTO stops VALUES('A',50.0,20.0),('B',50.01,20.01);
        INSERT INTO stop_times VALUES('trip-a','A',30000,30000,1),('trip-a','B',30600,30600,2);
    """)
    db.commit()
    db.close()
    monkeypatch.setattr(paths, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(store, "available_feeds", lambda: ["sample-city"])
    client = TestClient(app)
    response = client.get("/demo/replay/sample-city", params={"date": "2030-06-03", "mode": "tram"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "tram"
    assert data["active_trips"] > 0
    assert data["trips"]
    assert len(data["trips"]) <= 800
    assert all(len(t["points"]) >= 2 for t in data["trips"])
    assert all(len(p) == 3 for t in data["trips"] for p in t["points"])
    assert client.get("/demo/replay/sample-city", params={"date": "2030-06-03", "mode": "invalid"}).status_code == 404


def test_replay_controls_are_local_and_offline():
    client = TestClient(app)
    html = client.get("/demo").text
    js = client.get("/static/demo.js").text
    assert 'id="replay-position"' in html
    assert 'id="replay-speed"' in html
    assert "/demo/replay/" in js
    assert "replayPosition(points,sec)" in js


def test_buildings_are_opt_in_and_use_dark_style_vector_source():
    client = TestClient(app)
    html = client.get("/demo").text
    js = client.get("/static/demo.js").text
    assert 'id="buildings-button" type="button" aria-pressed="false"' in html
    assert "'source-layer':'building'" in js
    assert "type:'fill-extrusion'" in js
    assert "'fill-extrusion-height'" in js
    assert "map.removeLayer('demo-buildings')" in js
