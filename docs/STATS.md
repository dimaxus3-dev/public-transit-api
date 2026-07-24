# 📊 Network statistics

Everything currently ingested on the reference instance — generated 2026-07-24, always reproducible with `python3 scripts/stops_report.py`; a running server reports the same numbers live at `GET /stats`.

| City | Country | Routes | **Stops** | Trips/day sched. | Shapes | Full stop table |
|---|:---:|---:|---:|---:|---:|---|
| **Wien** | AT | 695 | **4,259** | 300,366 | 4,761 | [all 4,259 stops →](stops/mdb-648.md) |
| **Szczecin** | PL | 97 | **1,633** | 17,300 | 525 | [all 1,633 stops →](stops/szczecin-zditm.md) |
| **New York City Subway** | US | 29 | **1,488** | 20,309 | 257 | [all 1,488 stops →](stops/nyc-subway.md) |
| **Kielce** | PL | 56 | **1,382** | 24,086 | 1,237 | [all 1,382 stops →](stops/kielce.md) |
| **Venice** | IT | 25 | **150** | 10,051 | 187 | [all 150 stops →](stops/mdb-1063.md) |
| **Total (5 cities)** | | **902** | **8,912** | **372,112** | **6,967** | |

Beyond the ingested demo set, the registry holds **1500+ feeds in 71 countries** — ingest any of them (`python -m app.ingest <id>`) and it appears here and in `GET /stats` automatically.