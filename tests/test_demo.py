"""Offline checks for the MapLibre demo shell and its local assets."""

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
