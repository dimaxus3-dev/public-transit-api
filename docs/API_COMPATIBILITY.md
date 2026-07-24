# GTFS compatibility matrix

Honest scope: what this backend reads, what it partially uses, and what it
deliberately does not support (yet). "Silently mishandling" unknown
structures is worse than declaring them unsupported.

## GTFS Static

| File / capability | Status | Notes |
|---|:---:|---|
| `routes.txt`, `trips.txt`, `stop_times.txt` | ✅ Full | core of every artifact |
| `stops.txt` | ✅ Full | incl. `parent_station` (departure boards expand child platforms) |
| `calendar.txt` + `calendar_dates.txt` | ✅ Full | additions and removals resolved per service day |
| Times past midnight (`24:xx`, `25:xx`…) | ✅ Full | day-offset handling in boards and router |
| `agency.txt` timezone | ✅ Full | captured at ingest; all times are feed-local |
| `shapes.txt` | 🟡 Optional | best (longest) shape per route/direction; feeds without shapes still work (no line geometry) |
| Route colors | ✅ Full | per-route, with sensible fallbacks |
| `frequencies.txt` | ❌ Unsupported | frequency-based trips are not expanded — planned |
| `transfers.txt` | 🟡 Partial | ignored; walking transfers are distance-based (250 m radius) instead |
| `pathways.txt` / station routing | ❌ Unsupported | |
| Fares (`fare_*.txt`, fare products) | ❌ Unsupported | out of scope |
| Wheelchair / accessibility routing | ❌ Unsupported | fields are not evaluated |
| Multi-agency feeds | 🟡 Partial | routes/trips fully served; first agency's timezone wins |

## GTFS-Realtime

| Feed | Status | Notes |
|---|:---:|---|
| VehiclePositions | ✅ Supported | positions, bearing, label; joined with static route metadata |
| TripUpdates | ✅ Supported | per-trip delay (trip-level or first stop-time event) feeds boards **and** the router |
| Alerts | 🟡 Partial | fetched/health-checked for curated feeds; not yet exposed via a public endpoint |
| Trip cancellations (`schedule_relationship`) | ❌ Unsupported | cancelled trips still appear from static data — planned |
| Per-stop delay propagation | 🟡 Partial | one representative delay per trip, not per stop |

## API stability

The HTTP surface is versioned by SemVer of the project. Within `1.x`:
response **fields are only added, never removed or renamed**; errors stay
RFC 7807; existing query parameters keep their semantics. Breaking changes
mean `2.0.0`.
