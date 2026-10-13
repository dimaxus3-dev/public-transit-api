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
