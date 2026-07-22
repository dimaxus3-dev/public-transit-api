# 🚇 City Transit API

**A keyless FastAPI backend for city public transport.** It turns official
**GTFS** feeds into map-ready line geometry + stops, plans door-to-door city
journeys (walk → ride → transfer → ride → walk) with a stdlib router, and
overlays **live** vehicle positions and delays where a city publishes
GTFS-Realtime. No API keys. No database. Artifacts are flat files.

<p>
  <img src="https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white" alt="fastapi">
  <img src="https://img.shields.io/badge/API%20keys-0%20required-brightgreen" alt="keyless">
  <img src="https://img.shields.io/badge/cities-17%20live-blue" alt="cities">
  <img src="https://img.shields.io/badge/dependencies-fastapi%20%2B%20uvicorn-lightgrey" alt="deps">
</p>

> **Public transport only** — city trams, buses, metro, urban & national rail.
> Verified live **2026-07-22**. Re-check any time:
> `python3 scripts/feeds_status.py`.

---

## 🚦 Feed status — what works & what doesn't

Every GTFS feed is the *only* external dependency here, so "checking the APIs"
means checking the feeds. Live-verified with
[`scripts/feeds_status.py`](scripts/feeds_status.py):
✅ = HTTP 200 · ➖ = needs a provider key · ❌ = down.

| City | Country | Static GTFS | Realtime | Status |
|---|---|---|:---:|:---:|
| **Szczecin** (ZDiTM) | 🇵🇱 PL | 3.9 MB | 📡 vehicles + trips + alerts | ✅ |
| **Warszawa** (ZTM) | 🇵🇱 PL | 100 MB | — | ✅ |
| **GZM / Katowice** (Silesia) | 🇵🇱 PL | 44 MB | — | ✅ |
| **Bydgoszcz** | 🇵🇱 PL | 2.5 MB | — | ✅ |
| **Toruń** | 🇵🇱 PL | 2.0 MB | — | ✅ |
| **Rzeszów** | 🇵🇱 PL | 3.9 MB | — | ✅ |
| **Lublin** | 🇵🇱 PL | 5.6 MB | — | ✅ |
| **Radom** | 🇵🇱 PL | 2.4 MB | — | ✅ |
| **Kielce** | 🇵🇱 PL | 7.9 MB | — | ✅ |
| **PKP** (national rail) | 🇵🇱 PL | 28 MB | — | ✅ |
| **Berlin / Brandenburg** (VBB) | 🇩🇪 DE | 75 MB | — | ✅ |
| **DB long-distance** | 🇩🇪 DE | 0.4 MB | — | ✅ |
| **DB regional rail** | 🇩🇪 DE | 10 MB | — | ✅ |
| **New York City Subway** (MTA) | 🇺🇸 US | 5.6 MB | — | ✅ |
| **Boston** (MBTA) | 🇺🇸 US | 18 MB | — | ✅ |
| **Portland, OR** (TriMet) | 🇺🇸 US | 38 MB | — | ✅ |
| **Chicago** (CTA) | 🇺🇸 US | 68 MB | — | ✅ |
| **Bay Area** (511) | 🇺🇸 US | — | — | ➖ needs 511 key |

**17 / 18 feeds live · 3 countries · 15 cities + 3 rail networks.**

```bash
python3 scripts/feeds_status.py     # prints this table, live, per city
```

Add a city by registering a verified `gtfs_static_url` in
[`feeds.json`](feeds.json) and running `python -m app.ingest <id>`.
**Don't invent feed URLs** — only add ones you've confirmed.

---

## 🌍 Coverage

| 🇵🇱 Poland | 🇩🇪 Germany | 🇺🇸 USA |
|---|---|---|
| Szczecin · Warszawa · Katowice/GZM · Bydgoszcz · Toruń · Rzeszów · Lublin · Radom · Kielce · PKP rail | Berlin/Brandenburg (VBB) · DB long-distance · DB regional rail | NYC Subway · Boston · Portland · Chicago · (Bay Area\*) |

<sub>\* Bay Area 511 needs a free provider API key before it can be ingested.</sub>

---

## 🔌 Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness + which feeds are ingested |
| `GET /cities` | Ingested cities + center coords (map picker) |
| `GET /routes?city=` | Routes in a city (filter by `mode`) |
| `GET /routes/{city}/{route_id}/geometry` | One route's line as GeoJSON |
| `GET /routes/{city}/{route_id}/stops` | Ordered stops of a route/direction |
| `GET /map/layers?city=` | What to draw + where to fetch it |
| `GET /map/{city}/lines.geojson` | Full line layer for the map |
| `GET /stops?city=` · `/stops/nearby` · `/stops/search` | Stops (all / by radius / by name) |
| `GET /stops/{city}/{stop_id}/departures` | Next departures ("My Stop" board), live |
| `GET /journey` | **Plan A→B** — walk + rides + transfers, live delays |
| `GET /vehicles/live?city=` | Live vehicle positions (GTFS-RT feeds) |

Interactive docs at `/docs` once the server is up.

---

## 🧭 How it works

```
GTFS zip ──▶ app/ingest.py ──▶ data/<city>/  { lines.geojson · stops.json · gtfs.sqlite }
                                     │
                                     ▼
   app/store.py     geometry, stops, nearby        ◀── FastAPI (app/main.py)
   app/schedule.py  service calendar, departures
   app/routing.py   Connection Scan A→B journeys
   app/realtime.py  GTFS-RT vehicles + delays (stdlib protobuf reader)
```

- **Routing** is a **Connection Scan Algorithm** over the day's GTFS
  connections — stdlib-only, an active city day scans in well under a second.
- **Realtime** parses the GTFS-RT protobuf with a tiny built-in wire reader —
  no `gtfs-realtime-bindings`, no protobuf dependency.
- **Geometry** dedupes to the longest shape per (route, direction) so the map
  draws one clean line per route, not dozens of overlapping variants.
- **Timezones:** GTFS times are local wall-clock, so departures use each feed's
  own timezone, never the server's clock.

---

## ▶️ Run

```bash
pip install -r requirements.txt        # fastapi + uvicorn, nothing else
python -m app.ingest szczecin-zditm    # download + build one city (stdlib only)
uvicorn app.main:app --reload          # → http://127.0.0.1:8000/docs
```

```bash
curl "http://127.0.0.1:8000/cities"
curl "http://127.0.0.1:8000/journey?city=szczecin-zditm&from_lat=53.428&from_lon=14.552&to_lat=53.44&to_lon=14.49"
```

No keys or config required. `data/` (ingested artifacts) is generated and
gitignored — regenerate with `app.ingest`.

---

<div align="center">

**Made by Dmytro Serohyn**

<sub>Keyless · GTFS static + realtime · 17 cities live · verified 2026-07-22</sub>

</div>
