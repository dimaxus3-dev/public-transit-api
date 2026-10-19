"""Offline checks for the /world top-100 coverage page and its data."""

from fastapi.testclient import TestClient

from app import world
from app.main import app


def test_world_page_and_assets():
    client = TestClient(app)
    page = client.get("/world")
    assert page.status_code == 200
    assert "/static/world.js" in page.text
    assert "/static/world-land.svg" in page.text
    assert 'id="grid"' in page.text
    js = client.get("/static/world.js")
    assert js.status_code == 200
    assert "/world/cities" in js.text
    assert "innerHTML" not in js.text  # registry text is rendered as text only
    assert client.get("/static/world.css").status_code == 200
    assert client.get("/static/world-land.svg").status_code == 200


def test_world_cities_payload():
    data = TestClient(app).get("/world/cities").json()
    cities = data["cities"]
    assert len(cities) == 100
    assert [c["rank"] for c in cities] == list(range(1, 101))
    s = data["summary"]
    assert s["covered"] + s["uncovered"] == 100
    assert s["covered"] == sum(1 for c in cities if c["feeds"])
    assert s["feeds"] == sum(len(c["feeds"]) for c in cities)
    for c in cities:
        assert 0 <= c["x"] <= data["map"]["width"]
        assert 0 <= c["y"] <= data["map"]["height"]
        assert all(f["km"] <= data["radius_km"] for f in c["feeds"])
        assert [f["km"] for f in c["feeds"]] == sorted(f["km"] for f in c["feeds"])


def test_equal_earth_projection_frame():
    # Origin sits at the frame's centre line; the antimeridian at the edges.
    x0, _ = world.project(0, 0)
    assert abs(x0 - world.MAP_W / 2) < 1
    xl, _ = world.project(0, -180)
    xr, _ = world.project(0, 180)
    assert xl < 5 and xr > world.MAP_W - 5
    _, y_n = world.project(60, 0)
    _, y_s = world.project(-60, 0)
    assert y_n < y_s
