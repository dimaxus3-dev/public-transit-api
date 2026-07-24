#!/usr/bin/env python3
"""Deep end-to-end verification of world-catalog feeds.

    python3 scripts/deep_check.py [N]      # default 120 sampled feeds

"HTTP 200" alone doesn't prove a feed works. This script takes a random
sample of world feeds and pushes each through the FULL funnel:

    reachable   HEAD answers 200 and size is within the download cap
    ingested    download → validate → parse → schedule DB → atomic swap all OK
    routable    the ingested feed has service today and the CSA router
                actually plans a ride along one of its own trips

Results land in docs/DEEP_CHECK.md + docs/deep_check.json. Artifacts of
checked feeds are deleted afterwards (disk stays clean); ingest runs in
subprocesses with a hard timeout so one pathological feed can't wedge the run.
"""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
MAX_MB = 25  # skip giant feeds — bandwidth-friendly sample
INGEST_TIMEOUT = 240  # s per feed, subprocess hard limit


def head_size(url: str) -> tuple[int, int]:
    """(http_code, size_bytes) via HEAD (0 size when unknown)."""
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "public-transit-api/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, int(r.headers.get("Content-Length") or 0)
    except Exception:
        return 0, 0


def routable_smoke(fid: str) -> tuple[bool, str]:
    """Plan a ride along one of the feed's own trips, today, in-process."""
    from app import routing

    db_path = os.path.join(DATA, fid, "gtfs.sqlite")
    if not os.path.exists(db_path):
        return False, "no schedule db"
    db = sqlite3.connect(db_path)
    row = db.execute("""
        SELECT st.trip_id, MIN(st.seq), MAX(st.seq) FROM stop_times st
        GROUP BY st.trip_id HAVING COUNT(*) >= 3 LIMIT 1""").fetchone()
    if not row:
        db.close()
        return False, "no multi-stop trips"
    trip_id, lo, hi = row
    pts = db.execute(
        """
        SELECT s.lat, s.lon FROM stop_times st JOIN stops s ON st.stop_id = s.stop_id
        WHERE st.trip_id = ? AND st.seq IN (?, ?) ORDER BY st.seq""",
        (trip_id, lo, hi),
    ).fetchall()
    db.close()
    if len(pts) < 2:
        return False, "trip stops unresolved"
    (alat, alon), (blat, blon) = pts[0], pts[-1]
    routing._stops.cache_clear()
    routing._footpaths.cache_clear()
    routing._day_connections.cache_clear()
    for hour in (8, 13, 17):
        when = dt.datetime.now().replace(hour=hour, minute=0, second=0)
        try:
            if routing.plan(fid, alat, alon, blat, blon, when):
                return True, ""
        except Exception as e:  # noqa: BLE001
            return False, f"router error: {type(e).__name__}"
    return False, "no service today (expired/inactive calendar?)"


def check(feed: dict) -> dict:
    fid, url = feed["id"], feed["gtfs_static_url"]
    rec = {
        "id": fid,
        "country": feed.get("country"),
        "city": feed.get("city_region"),
        "reachable": False,
        "ingested": False,
        "routable": False,
        "note": "",
    }
    code, size = head_size(url)
    if code != 200:
        rec["note"] = f"HTTP {code or 'error'}"
        return rec
    if size > MAX_MB * 1_000_000:
        rec["note"] = f"skipped: {size // 1_000_000} MB > {MAX_MB} MB sample cap"
        rec["reachable"] = True
        return rec
    rec["reachable"] = True
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "app.ingest", fid],
            capture_output=True,
            text=True,
            timeout=INGEST_TIMEOUT,
            cwd=ROOT,
        )
        if proc.returncode != 0:
            err = (proc.stderr.strip().splitlines() or ["ingest failed"])[-1]
            rec["note"] = err[:140]
            return rec
        rec["ingested"] = True
        ok, why = routable_smoke(fid)
        rec["routable"], rec["note"] = ok, why
    except subprocess.TimeoutExpired:
        rec["note"] = f"ingest exceeded {INGEST_TIMEOUT}s"
    except Exception as e:  # noqa: BLE001
        rec["note"] = f"{type(e).__name__}: {str(e)[:120]}"
    finally:
        if fid not in KEEP:
            shutil.rmtree(os.path.join(DATA, fid), ignore_errors=True)
        shutil.rmtree(os.path.join(DATA, f".build-{fid}"), ignore_errors=True)
    return rec


KEEP: set = set()


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "120"
    from app import registry

    everything = [
        f for f in registry.load().values() if str(f.get("gtfs_static_url", "")).startswith("http")
    ]
    if arg == "all":
        sample = everything  # the full registry — hours of downloads
    else:
        random.seed(20260724)
        sample = random.sample(everything, min(int(arg), len(everything)))

    # Never delete feeds that were already ingested before this run (the
    # instance's live cities) — only clean up what this check itself built.
    KEEP.update(os.listdir(DATA) if os.path.isdir(DATA) else [])

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for i, rec in enumerate(pool.map(check, sample), 1):
            results.append(rec)
            stage = (
                "routable"
                if rec["routable"]
                else "ingested"
                if rec["ingested"]
                else "reachable"
                if rec["reachable"]
                else "dead"
            )
            print(
                f"[{i:>3}/{len(sample)}] {stage:<9} {rec['id']:<10} "
                f"{(rec['city'] or '')[:34]:<34} {rec['note'][:60]}",
                file=sys.stderr,
            )

    date = time.strftime("%Y-%m-%d")
    r = len([x for x in results if x["reachable"]])
    g = len([x for x in results if x["ingested"]])
    t = len([x for x in results if x["routable"]])
    N = len(results)

    scope = "**the ENTIRE registry** — all" if arg == "all" else "a random sample of"
    L = [
        "# 🔬 Deep check — does a feed actually WORK, not just answer HTTP?\n",
        f"{scope} **{N} feeds**, each pushed through the "
        f"full pipeline on **{date}** (feeds over {MAX_MB} MB marked "
        "`skipped` — download cap keeps the run bandwidth-sane):\n",
        "| Stage | Feeds | % of sample |",
        "|---|---:|---:|",
        f"| 📡 Reachable (HTTP 200) | {r}/{N} | {100 * r // N} % |",
        f"| 📦 Valid GTFS, ingested end-to-end | {g}/{N} | {100 * g // N} % |",
        f"| 🗺️ Routable (CSA planned a real trip today) | {t}/{N} | {100 * t // N} % |",
        "\n> `ingested` proves download → zip validation → parse → schedule DB "
        "→ atomic swap. `routable` additionally proves the feed has service "
        "today and the journey planner finds a ride along the feed's own "
        "trips. Non-routable ingests are usually expired calendars — the "
        "feed's own data problem, not a pipeline failure.\n",
        "<details><summary>Every sampled feed</summary>\n",
        "| Feed | City | Reach | Ingest | Route | Note |",
        "|---|---|:---:|:---:|:---:|---|",
    ]
    for x in sorted(results, key=lambda x: (-(x["routable"]), -(x["ingested"]), x["id"])):

        def m(b):
            return "✅" if b else "—"

        L.append(
            f"| `{x['id']}` | {(x['city'] or '')[:30]} | {m(x['reachable'])} "
            f"| {m(x['ingested'])} | {m(x['routable'])} | {x['note'][:70]} |"
        )
    repro = "all" if arg == "all" else str(N)
    L += [
        "\n</details>\n",
        f"\n<sub>Reproduce: `python3 scripts/deep_check.py {repro}` · "
        "numeric samples use a fixed seed, so they are stable between runs.</sub>",
    ]

    os.makedirs(DOCS, exist_ok=True)
    open(os.path.join(DOCS, "DEEP_CHECK.md"), "w").write("\n".join(L))
    json.dump(
        {
            "date": date,
            "sample": N,
            "reachable": r,
            "ingested": g,
            "routable": t,
            "results": results,
        },
        open(os.path.join(DOCS, "deep_check.json"), "w"),
        ensure_ascii=False,
        indent=1,
    )
    print(
        f"\nfunnel: {r} reachable -> {g} ingested -> {t} routable "
        f"(of {N}) · docs/DEEP_CHECK.md written"
    )


if __name__ == "__main__":
    main()
