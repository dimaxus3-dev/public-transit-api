#!/usr/bin/env python3
"""Generate network statistics + a full stop table for every ingested city.

    python3 scripts/stops_report.py

Writes:
    docs/STATS.md            summary: per-city routes/stops/trips + totals
    docs/stops/<feed>.md     the COMPLETE stop table of that city
                             (id, name, lat, lon, OSM link)

Pure stdlib; reads the same artifacts the API serves, so the numbers always
match what a running instance reports at GET /stats.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import registry  # noqa: E402
from app.paths import DATA_DIR  # noqa: E402

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
STOPS_DIR = os.path.join(DOCS, "stops")
PAGE = 2000  # stops per page — keeps every file under GitHub's render limit


def ingested_feeds() -> list[str]:
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(
        d for d in os.listdir(DATA_DIR) if os.path.exists(os.path.join(DATA_DIR, d, "summary.json"))
    )


def main() -> None:
    feeds_meta = registry.load()
    os.makedirs(STOPS_DIR, exist_ok=True)
    date = time.strftime("%Y-%m-%d")

    rows = []
    totals = {"routes": 0, "stops": 0, "trips": 0, "shapes": 0}
    for fid in ingested_feeds():
        with open(os.path.join(DATA_DIR, fid, "summary.json"), encoding="utf-8") as fh:
            s = json.load(fh)
        with open(os.path.join(DATA_DIR, fid, "stops.json"), encoding="utf-8") as fh:
            stops = json.load(fh)
        meta = feeds_meta.get(fid, {})
        city = meta.get("city_region", fid)
        rows.append((fid, city, meta.get("country") or "—", s, len(stops)))
        for k in totals:
            totals[k] += s.get(k, 0)

        # Full per-city stop table, paginated so every page stays under
        # GitHub's ~512 KB markdown render limit.
        ordered = sorted(stops, key=lambda x: x["name"])
        pages = [ordered[i : i + PAGE] for i in range(0, len(ordered), PAGE)] or [[]]
        for pno, chunk in enumerate(pages, 1):
            suffix = "" if pno == 1 else f"-p{pno}"
            nav = " · ".join(
                f"**part {n}**" if n == pno else f"[part {n}]({fid}{'' if n == 1 else f'-p{n}'}.md)"
                for n in range(1, len(pages) + 1)
            )
            first, last = pno * PAGE - PAGE + 1, min(pno * PAGE, len(ordered))
            L = [
                f"# 🚏 {city} — all {len(ordered)} stops"
                + (f" (part {pno}/{len(pages)}: {first}–{last})" if len(pages) > 1 else "")
                + "\n",
                f"Feed `{fid}` · generated {date} from `data/{fid}/stops.json` "
                "(the exact artifact the API serves)."
                + (f" Pages: {nav}\n" if len(pages) > 1 else "\n"),
                "| # | Stop | ID | Lat | Lon | Map |",
                "|---:|---|---|---:|---:|---|",
            ]
            for i, st in enumerate(chunk, first):
                osm = (
                    f"https://www.openstreetmap.org/?mlat={st['lat']}&mlon={st['lon']}"
                    f"#map=18/{st['lat']}/{st['lon']}"
                )
                name = st["name"].replace("|", "\\|")
                L.append(
                    f"| {i} | {name} | `{st['id']}` | {st['lat']:.5f} | {st['lon']:.5f} "
                    f"| [🗺]({osm}) |"
                )
            L.append("\n<sub>Regenerate: `python3 scripts/stops_report.py`</sub>")
            with open(os.path.join(STOPS_DIR, f"{fid}{suffix}.md"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(L))
        print(f"[{fid}] {len(ordered)} stops -> docs/stops/{fid}.md ({len(pages)} page(s))")

    rows.sort(key=lambda r: -r[4])
    L = [
        "# 📊 Network statistics\n",
        f"Everything currently ingested on the reference instance — generated "
        f"{date}, always reproducible with `python3 scripts/stops_report.py`; "
        "a running server reports the same numbers live at `GET /stats`.\n",
        "| City | Country | Routes | **Stops** | Trips/day sched. | Shapes | Full stop table |",
        "|---|:---:|---:|---:|---:|---:|---|",
    ]
    for fid, city, country, s, nstops in rows:
        L.append(
            f"| **{city}** | {country} | {s.get('routes', 0)} | **{nstops:,}** "
            f"| {s.get('trips', 0):,} | {s.get('shapes', 0):,} "
            f"| [all {nstops:,} stops →](stops/{fid}.md) |"
        )
    L.append(
        f"| **Total ({len(rows)} cities)** | | **{totals['routes']:,}** "
        f"| **{totals['stops']:,}** | **{totals['trips']:,}** | **{totals['shapes']:,}** | |"
    )
    L += [
        "",
        "Beyond the ingested demo set, the registry holds **1500+ feeds in 71 "
        "countries** — ingest any of them (`python -m app.ingest <id>`) and it "
        "appears here and in `GET /stats` automatically.",
    ]
    with open(os.path.join(DOCS, "STATS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(
        f"\nTOTAL: {len(rows)} cities · {totals['routes']:,} routes · "
        f"{totals['stops']:,} stops · {totals['trips']:,} trips -> docs/STATS.md"
    )


if __name__ == "__main__":
    main()
