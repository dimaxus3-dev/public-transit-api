/**
 * Tiny zero-dependency JS/TS client for the City Transit API.
 * Works in the browser, Node 18+, Deno and Bun (uses fetch / EventSource).
 *
 *   import { TransitClient } from "./transit-client.js";
 *
 *   const t = new TransitClient("http://localhost:8000");
 *   const { feeds } = await t.feeds({ country: "IT" });
 *   await t.ingest("mdb-648");                        // activate Vienna
 *   const plan = await t.journey("szczecin-zditm",
 *     { fromLat: 53.428, fromLon: 14.552, toLat: 53.44, toLon: 14.49 });
 *
 *   // live vehicles on a map — one line:
 *   t.vehiclesStream("szczecin-zditm", frame => drawMarkers(frame.vehicles));
 */
export class TransitError extends Error {
  constructor(status, problem) {
    super(`HTTP ${status}: ${problem?.detail ?? "error"}`);
    this.status = status;
    this.problem = problem; // RFC 7807 body
  }
}

export class TransitClient {
  constructor(baseUrl = "http://localhost:8000", { apiKey = "" } = {}) {
    this.base = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  // ── discovery ──────────────────────────────────────────────────────────
  health()            { return this._get("/health"); }
  countries()         { return this._get("/countries"); }
  cities()            { return this._get("/cities"); }
  feeds(opts = {})    { return this._get("/feeds", opts); }
  ingest(feedId)      { return this._call("POST", `/feeds/${feedId}/ingest`); }

  // ── per-city data ──────────────────────────────────────────────────────
  routes(city, mode)  { return this._get("/routes", { city, mode }); }
  routeGeometry(city, routeId) { return this._get(`/routes/${city}/${routeId}/geometry`); }
  stopsNearby(city, { lat, lng, radius = 500, limit = 50 } = {}) {
    return this._get("/stops/nearby", { city, lat, lng, radius, limit });
  }
  stopsSearch(city, q, limit = 12) { return this._get("/stops/search", { city, q, limit }); }
  departures(city, stopId, limit = 10) {
    return this._get(`/stops/${city}/${stopId}/departures`, { limit });
  }
  journey(city, { fromLat, fromLon, toLat, toLon, time } = {}) {
    return this._get("/journey", { city, from_lat: fromLat, from_lon: fromLon,
                                   to_lat: toLat, to_lon: toLon, time });
  }
  vehicles(city)      { return this._get("/vehicles/live", { city }); }

  /** Subscribe to the SSE stream; returns the EventSource (call .close() to stop). */
  vehiclesStream(city, onFrame, { interval = 5 } = {}) {
    const es = new EventSource(
      `${this.base}/vehicles/stream?city=${encodeURIComponent(city)}&interval=${interval}`);
    es.onmessage = (e) => onFrame(JSON.parse(e.data));
    return es;
  }

  // ── plumbing ───────────────────────────────────────────────────────────
  async _call(method, path, params) {
    const url = new URL(this.base + path);
    for (const [k, v] of Object.entries(params ?? {}))
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    const headers = { Accept: "application/json" };
    if (this.apiKey) headers["X-API-Key"] = this.apiKey;
    const resp = await fetch(url, { method, headers });
    const body = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new TransitError(resp.status, body);
    return body;
  }
  _get(path, params) { return this._call("GET", path, params); }
}
