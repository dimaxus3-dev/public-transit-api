#!/usr/bin/env python3
"""Import the world's GTFS feeds from the official MobilityData catalog.

    python3 scripts/import_catalog.py              # build feeds_world.json
    python3 scripts/import_catalog.py --verify 60  # + live-check a random sample

Pulls the MobilityData catalog (the registry behind mobilitydatabase.org,
~2400 GTFS feeds worldwide), keeps every ACTIVE feed that can be downloaded
WITHOUT an API key, and writes them to feeds_world.json. Every imported feed
becomes ingestable by id, exactly like a curated feeds.json entry:

    python -m app.ingest mdb-1866        # e.g. Rome, Italy

Prefers `urls.latest` — MobilityData's own stable mirror of each feed's most
recent zip — so imports don't break when an agency moves its download page.
stdlib only.
"""

from __future__ import annotations

import csv
import io
import json
import os
import random
import sys
import urllib.request

CATALOG_URL = "https://bit.ly/catalogs-csv"  # official MobilityData catalog CSV
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "feeds_world.json")


def fetch_catalog() -> list[dict]:
    req = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "public-transit-api/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return list(csv.DictReader(io.TextIOWrapper(r, encoding="utf-8-sig")))


def build(rows: list[dict]) -> list[dict]:
    feeds = []
    for r in rows:
        if r["data_type"] != "gtfs":
            continue
        if r["status"] in ("deprecated", "inactive"):
            continue
        if r["urls.authentication_type"] not in ("", "0"):
            continue  # needs an API key — out of scope here
        url = r["urls.latest"] or r["urls.direct_download"]
        if not url:
            continue
        try:
            lat = (
                float(r["location.bounding_box.minimum_latitude"])
                + float(r["location.bounding_box.maximum_latitude"])
            ) / 2
            lon = (
                float(r["location.bounding_box.minimum_longitude"])
                + float(r["location.bounding_box.maximum_longitude"])
            ) / 2
        except ValueError:
            lat = lon = None
        city = r["location.municipality"] or r["location.subdivision_name"] or r["provider"]
        feeds.append(
            {
                "id": f"mdb-{r['mdb_source_id']}",
                "country": r["location.country_code"],
                "city_region": city,
                "agency_provider": r["provider"],
                "name": r["name"],
                "gtfs_static_url": url,
                "lat": lat,
                "lon": lon,
                "source": "mobility-database",
            }
        )
    return feeds


def verify_sample(feeds: list[dict], n: int) -> None:
    """HEAD-check a random sample so the README numbers stay honest."""
    sample = random.sample(feeds, min(n, len(feeds)))
    ok = 0
    for f in sample:
        try:
            req = urllib.request.Request(
                f["gtfs_static_url"],
                method="HEAD",
                headers={"User-Agent": "public-transit-api/0.1"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                good = 200 <= r.status < 400
        except Exception:
            good = False
        ok += good
        print(f"  {'✅' if good else '❌'} {f['id']:<10} {f['country']:<3} {f['city_region'][:40]}")
    print(f"\n  sample health: {ok}/{len(sample)} reachable")


def main() -> None:
    print("downloading MobilityData catalog…")
    rows = fetch_catalog()
    feeds = build(rows)
    countries = sorted({f["country"] for f in feeds if f["country"]})
    json.dump(
        {
            "generated_from": "MobilityData catalog",
            "count": len(feeds),
            "countries": len(countries),
            "feeds": feeds,
        },
        open(OUT, "w"),
        ensure_ascii=False,
        indent=1,
    )
    print(
        f"wrote {os.path.relpath(OUT)}: {len(feeds)} keyless GTFS feeds "
        f"in {len(countries)} countries"
    )
    per = {}
    for f in feeds:
        per[f["country"]] = per.get(f["country"], 0) + 1
    top = sorted(per.items(), key=lambda kv: -kv[1])[:12]
    print("top countries:", ", ".join(f"{c}:{n}" for c, n in top))

    if "--verify" in sys.argv:
        n = int(sys.argv[sys.argv.index("--verify") + 1])
        print(f"\nlive-checking a random sample of {n}…")
        verify_sample(feeds, n)


if __name__ == "__main__":
    main()
