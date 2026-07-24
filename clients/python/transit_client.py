"""Tiny zero-dependency Python client for the City Transit API.

    from transit_client import TransitClient

    t = TransitClient("http://localhost:8000")
    for f in t.feeds(country="IT")["feeds"]:
        print(f["city"], "✅" if f["ingested"] else "·")

    t.ingest("mdb-648")                      # activate Vienna
    plan = t.journey("szczecin-zditm", 53.428, 14.552, 53.44, 14.49)
    print(plan["itineraries"][0]["duration_min"], "min")

stdlib only — copy this one file into your project and go.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class TransitError(RuntimeError):
    """Raised for any non-2xx response; carries the RFC 7807 problem body."""

    def __init__(self, status: int, problem: dict):
        self.status, self.problem = status, problem
        super().__init__(f"HTTP {status}: {problem.get('detail', problem)}")


class TransitClient:
    def __init__(self, base_url: str = "http://localhost:8000",
                 api_key: str = "", timeout: float = 30.0):
        self.base = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    # ── discovery ────────────────────────────────────────────────────────────
    def health(self) -> dict:
        return self._get("/health")

    def feeds(self, country: str = "", q: str = "", limit: int = 100,
              offset: int = 0) -> dict:
        return self._get("/feeds", country=country or None, q=q or None,
                         limit=limit, offset=offset)

    def countries(self) -> dict:
        return self._get("/countries")

    def cities(self) -> list:
        return self._get("/cities")

    def ingest(self, feed_id: str) -> dict:
        return self._post(f"/feeds/{feed_id}/ingest")

    # ── per-city data ────────────────────────────────────────────────────────
    def routes(self, city: str, mode: str = "") -> list:
        return self._get("/routes", city=city, mode=mode or None)

    def route_geometry(self, city: str, route_id: str) -> dict:
        return self._get(f"/routes/{city}/{route_id}/geometry")

    def stops_nearby(self, city: str, lat: float, lng: float,
                     radius: float = 500, limit: int = 50) -> list:
        return self._get("/stops/nearby", city=city, lat=lat, lng=lng,
                         radius=radius, limit=limit)

    def stops_search(self, city: str, q: str, limit: int = 12) -> list:
        return self._get("/stops/search", city=city, q=q, limit=limit)

    def departures(self, city: str, stop_id: str, limit: int = 10) -> dict:
        return self._get(f"/stops/{city}/{stop_id}/departures", limit=limit)

    def journey(self, city: str, from_lat: float, from_lon: float,
                to_lat: float, to_lon: float, time: str = "") -> dict:
        return self._get("/journey", city=city, from_lat=from_lat,
                         from_lon=from_lon, to_lat=to_lat, to_lon=to_lon,
                         time=time or None)

    def vehicles(self, city: str) -> dict:
        return self._get("/vehicles/live", city=city)

    def vehicles_stream(self, city: str, interval: float = 5.0):
        """Yield one dict per SSE frame — an infinite generator:

            for frame in t.vehicles_stream("szczecin-zditm"):
                print(frame["count"], "vehicles on the map")
        """
        url = f"{self.base}/vehicles/stream?" + urllib.parse.urlencode(
            {"city": city, "interval": interval})
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=None) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if line.startswith("data: "):
                    yield json.loads(line[6:])

    # ── plumbing ─────────────────────────────────────────────────────────────
    def _headers(self) -> dict:
        h = {"User-Agent": "transit-client-py/1.0", "Accept": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    def _call(self, method: str, path: str, **params):
        clean = {k: v for k, v in params.items() if v is not None}
        url = f"{self.base}{path}"
        if clean:
            url += "?" + urllib.parse.urlencode(clean)
        req = urllib.request.Request(url, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                problem = json.loads(e.read().decode("utf-8"))
            except Exception:  # noqa: BLE001
                problem = {"detail": str(e)}
            raise TransitError(e.code, problem) from None

    def _get(self, path: str, **params):
        return self._call("GET", path, **params)

    def _post(self, path: str, **params):
        return self._call("POST", path, **params)
