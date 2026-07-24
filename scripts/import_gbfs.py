#!/usr/bin/env python3
"""Import the world's shared-mobility systems (GBFS) from the official catalog.

    python3 scripts/import_gbfs.py

GBFS is the open standard for bike/scooter/moped sharing (1500+ systems
worldwide publish it). The MobilityData catalog (`systems.csv`) is the
authoritative registry; this script keeps every system that needs NO
authentication and writes feeds_gbfs.json. stdlib only.
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.request

CATALOG = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"
OUT = os.path.join(os.path.dirname(__file__), "..", "feeds_gbfs.json")


def main() -> None:
    req = urllib.request.Request(CATALOG, headers={"User-Agent": "public-transit-api/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        rows = list(csv.DictReader(io.TextIOWrapper(r, encoding="utf-8-sig")))

    systems = []
    for row in rows:
        if row.get("Authentication Type", "").strip():
            continue  # needs credentials — out of scope for a keyless API
        url = row.get("Auto-Discovery URL", "").strip()
        if not url.startswith("http"):
            continue
        systems.append(
            {
                "system_id": row["System ID"].strip(),
                "name": row["Name"].strip(),
                "location": row["Location"].strip(),
                "country": row["Country Code"].strip().upper(),
                "url": url,
                "versions": row.get("Supported Versions", "").strip(),
            }
        )

    countries = sorted({s["country"] for s in systems if s["country"]})
    json.dump(
        {
            "generated_from": "MobilityData GBFS systems.csv",
            "generated_at": time.strftime("%Y-%m-%d"),
            "count": len(systems),
            "countries": len(countries),
            "systems": systems,
        },
        open(OUT, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    per: dict = {}
    for s in systems:
        per[s["country"]] = per.get(s["country"], 0) + 1
    top = sorted(per.items(), key=lambda kv: -kv[1])[:10]
    print(
        f"wrote feeds_gbfs.json: {len(systems)} keyless GBFS systems in "
        f"{len(countries)} countries · top: " + ", ".join(f"{c}:{n}" for c, n in top)
    )


if __name__ == "__main__":
    main()
