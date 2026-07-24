# 🛴 Shared mobility & ⚡ EV charging — setup guide

Two more transport layers on top of public transit: scooters/city bikes
(GBFS, keyless) and EV charging stations (free keys). What they are, how to
turn them on, and what to watch out for.

---

## 🛴 Scooters, city bikes, mopeds — GBFS (no keys)

**GBFS** (General Bikeshare Feed Specification) is the open standard that
1500+ sharing systems publish — Dott, Bird, Bolt, Lime, nextbike, city bike
schemes. Each system exposes a public `gbfs.json` with sub-feeds: docked
stations (`station_information`/`station_status`), dockless vehicles with
battery level (`vehicle_status`, formerly `free_bike_status`), vehicle types
and pricing plans. Current spec: v3.0; v1/v2 feeds are still common and this
API reads all of them.

**Registry.** `feeds_gbfs.json` is imported from the authoritative
[MobilityData `systems.csv`](https://github.com/MobilityData/gbfs/blob/master/systems.csv)
catalog, keeping only systems that need **no authentication** — currently
**1515 systems in 48 countries** (FR 269 · DE 242 · US 175 · PL 102 · NO 88 …).
Refresh any time:

```bash
python3 scripts/import_gbfs.py
```

**Use it:**

```bash
curl "localhost:8000/gbfs/systems?country=PL&q=szczecin"
# → dott-szczecin (Dott Szczecin)

curl "localhost:8000/gbfs/dott-szczecin"
# → 108 stations + 884 vehicles, each with lat/lon, battery %, range
```

Snapshots are cached 15 s and back off a dead operator for 60 s (stale frame
served up to 2 min) — the same degrade-don't-fail pattern as GTFS-RT.

**Direct operator endpoints** (bypass the registry if you know the city):

| Operator | Pattern |
|---|---|
| Dott | `https://gbfs.api.ridedott.com/public/v2/{city}/gbfs.json` |
| Bird | `https://mds.bird.co/gbfs` |
| Bolt | `https://mds.bolt.eu/gbfs/1` |
| Lime | `https://data.lime.bike/api/partners/v2/gbfs/{city}/gbfs.json` |
| nextbike | `https://gbfs.nextbike.net/maps/gbfs/v2/{system_id}/gbfs.json` |

**Caveats.** Coverage is uneven: Lime and Bolt operate in many cities where
they publish **no** open data. Best coverage is where regulators require it —
Norway, Switzerland, France (`transport.data.gouv.fr`), US cities. If a
system is missing from `/gbfs/systems`, it either requires auth or simply
doesn't publish.

---

## ⚡ EV charging — Open Charge Map + NREL (free keys)

Charging providers require (free) keys, so `GET /charging/nearby` activates
per key and answers 503 with instructions until one is set.

### Open Charge Map — global, ~300k locations

1. Register at [openchargemap.org](https://openchargemap.org) → **My Profile
   → my apps → Register An Application** → copy the key.
2. `export OCM_API_KEY=...` (or put it in docker-compose environment).
3. ```bash
   curl "localhost:8000/charging/nearby?lat=52.52&lng=13.405&radius_km=5"
   ```

Rules you MUST respect (and this API helps with):
- **Attribution is mandatory** — the data is CC BY 4.0. Every response
  carries an `attribution` string; display it in your UI.
- **Don't hammer the API** — OCM auto-bans abusive clients. This API caches
  responses for 2 minutes per rounded-coordinate cell, so identical map pans
  never hit OCM twice. For heavy traffic, OCM recommends importing their data
  dump and self-hosting a mirror.

### NREL — США/Канада, the best quality there

1. Free key at [api.data.gov](https://api.data.gov/signup/) (limit 1000 req/h).
2. `export NREL_API_KEY=...`
3. Same endpoint with `provider=nrel`, or automatically when OCM key is absent.

⚠️ **Domain migration:** NREL's `developer.nrel.gov` was retired in May 2026;
the default base here is `https://developer.nlr.gov` (verified live). If it
moves again, override with `NREL_API_BASE`. NREL also has a "stations along a
route" endpoint (`/api/alt-fuel-stations/v1/nearby-route.json`) — a natural
next step for the journey planner.

### Alternatives without keys

- **OpenStreetMap/Overpass** — `amenity=charging_station` with
  `socket:type2`, `socket:ccs`, power and `fee` tags. Global and free, but
  public Overpass servers are overloaded — fine for a one-off bulk export
  into your own DB, not for live mobile traffic.
- **Poland: EIPA (UDT)** — `eipa.udt.gov.pl`, the state registry of all
  public charging points with coordinates, live prices and availability;
  public CSV export (`;`-separated). Other EU countries expose equivalents
  via their National Access Points.

---

## Endpoint summary

| Endpoint | Purpose | Keys |
|---|---|---|
| `GET /gbfs/systems?country=&q=` | Browse 1515 sharing systems | none |
| `GET /gbfs/{system_id}` | Live stations + vehicles (battery, range) | none |
| `GET /charging/nearby?lat&lng&radius_km&provider=` | EV chargers around a point | `OCM_API_KEY` / `NREL_API_KEY` (free) |
