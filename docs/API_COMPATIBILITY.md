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
| Separate arrival/departure times (dwell) | ✅ Full | schema v2: connections ride `departure → arrival`; dwells can't shorten rides or fake transfers |
| `pickup_type` / `drop_off_type` | ✅ Full | no-boarding stops hidden from boards & unenterable; no-alighting stops can't end a leg |
| Route patterns (branches, short-turns, express) | ✅ Full | `/routes/{city}/{id}/patterns` + per-pattern stops/geometry |
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
| TripUpdates | ✅ Supported | full decode: per-stop arrival/departure delays, trip-level delay, feed timestamp |
| Alerts | 🟡 Partial | fetched/health-checked for curated feeds; not yet exposed via a public endpoint |
| Trip cancellations (`schedule_relationship`) | ✅ Supported | canceled trips hidden from boards and excluded from the router |
| Skipped stops (STU `SKIPPED`) | ✅ Supported | hidden from that stop's board |
| Added / unscheduled trips | 🟡 Partial | detected and exposed in the state model; not yet routed |
| Per-stop delay propagation | ✅ Supported | boards use exact per-stop delays; router uses the trip-level shift |
| Vehicle occupancy | ✅ Supported | `occupancy` on `/vehicles/*` (empty → full) |

## API stability

The HTTP surface is versioned by SemVer of the project. Within `1.x`:
response **fields are only added, never removed or renamed**; errors stay
RFC 7807; existing query parameters keep their semantics. Breaking changes
mean `2.0.0`.
