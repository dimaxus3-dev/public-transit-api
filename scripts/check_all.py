#!/usr/bin/env python3
"""Live-check EVERY registered feed — all curated + all world-catalog cities —
and publish the results as a pretty status page.

    python3 scripts/check_all.py            # writes docs/STATUS.md + docs/status.json

For every single city: HTTP code, response latency and feed size (HEAD, or a
1-byte ranged GET for servers that reject HEAD — the multi-MB zips are never
downloaded). ~1500 feeds check in a couple of minutes on 80 threads.
stdlib only. A weekly GitHub Action re-runs this so the page stays honest.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import registry  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
DOCS = os.path.join(ROOT, "docs")
UA = {"User-Agent": "public-transit-api/1.0 (+status check)"}


def probe(url: str, timeout: int = 12) -> tuple[int, int, str]:
    """(http_code, latency_ms, size_note) without downloading the feed."""
    t0 = time.time()
    for method, extra in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        req = urllib.request.Request(url, method=method, headers={**UA, **extra})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                ms = int((time.time() - t0) * 1000)
                size = (
                    r.headers.get("Content-Length")
                    or r.headers.get("Content-Range", "").split("/")[-1]
                )
                mb = f"{int(size) / 1_000_000:.1f} MB" if size and size.isdigit() else "—"
                return (200 if r.status in (200, 206) else r.status), ms, mb
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 501) and method == "HEAD":
                continue
            return e.code, int((time.time() - t0) * 1000), "—"
        except Exception:
            return 0, int((time.time() - t0) * 1000), "—"
    return 0, int((time.time() - t0) * 1000), "—"


def flag(cc: str) -> str:
    cc = (cc or "").upper()
    if len(cc) != 2 or not cc.isalpha():
        return "🏳️"
    return chr(0x1F1E6 + ord(cc[0]) - 65) + chr(0x1F1E6 + ord(cc[1]) - 65)


def check_all() -> list[dict]:
    feeds = [
        f for f in registry.load().values() if str(f.get("gtfs_static_url", "")).startswith("http")
    ]

    def one(f):
        code, ms, size = probe(f["gtfs_static_url"])
        return {
            "id": f["id"],
            "country": (f.get("country") or "?").strip().upper() or "?",
            "city": f.get("city_region") or f["id"],
            "agency": f.get("agency_provider") or "",
            "http": code,
            "ms": ms,
            "size": size,
            "ok": code == 200,
        }

    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as pool:
        futures = [pool.submit(one, f) for f in feeds]
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            out.append(fut.result())
            if i % 200 == 0:
                print(f"  …{i}/{len(feeds)} checked", file=sys.stderr)
    return out


def write_status(rows: list[dict]) -> None:
    os.makedirs(DOCS, exist_ok=True)
    date = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    alive = [r for r in rows if r["ok"]]
    pct = 100 * len(alive) // len(rows)
    med = int(statistics.median(r["ms"] for r in alive)) if alive else 0

    by_country: dict[str, list[dict]] = {}
    for r in rows:
        by_country.setdefault(r["country"], []).append(r)

    L: list[str] = []
    L.append("# 🌍 Live status — every city, every feed\n")
    L.append(
        f"**{len(rows)} feeds · {len(by_country)} countries · "
        f"{len(alive)} alive ({pct} %) · median response {med} ms** — "
        f"checked {date}\n"
    )
    L.append(
        "> Every row is a real measurement (HTTP code · latency · feed size), "
        "taken by [`scripts/check_all.py`](../scripts/check_all.py). "
        "A weekly GitHub Action refreshes this page automatically. "
        "✅ HTTP 200 · ❌ down / error\n"
    )

    L.append("\n## Summary by country\n")
    L.append("| Country | Feeds | ✅ Alive | ❌ Down | Median latency |")
    L.append("|---|---:|---:|---:|---:|")
    order = sorted(by_country.items(), key=lambda kv: -len(kv[1]))
    for cc, rs in order:
        a = [r for r in rs if r["ok"]]
        m = int(statistics.median(r["ms"] for r in a)) if a else 0
        L.append(f"| {flag(cc)} **{cc}** | {len(rs)} | {len(a)} | {len(rs) - len(a)} | {m} ms |")

    L.append("\n## Every city\n")
    L.append("<sub>Click a country to expand its full city table.</sub>\n")
    for cc, rs in order:
        a = sum(r["ok"] for r in rs)
        L.append(
            f"<details><summary>{flag(cc)} <b>{cc}</b> — {len(rs)} feeds, {a} alive</summary>\n"
        )
        L.append("| City / region | Feed | HTTP | Latency | Size | |")
        L.append("|---|---|:---:|---:|---:|:---:|")
        for r in sorted(rs, key=lambda x: (x["city"] or "").lower()):
            mark = "✅" if r["ok"] else "❌"
            http = str(r["http"]) if r["http"] else "ERR"
            city = (r["city"] or r["id"])[:48]
            L.append(f"| {city} | `{r['id']}` | {http} | {r['ms']} ms | {r['size']} | {mark} |")
        L.append("\n</details>\n")

    L.append("\n---\n")
    L.append(
        f"<sub>Generated {date} · `python3 scripts/check_all.py` reproduces "
        "this page · feeds that need a provider API key are excluded from "
        "the registry by design.</sub>\n"
    )

    with open(os.path.join(DOCS, "STATUS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    with open(os.path.join(DOCS, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "checked_at": date,
                "total": len(rows),
                "alive": len(alive),
                "median_ms": med,
                "feeds": sorted(rows, key=lambda r: r["id"]),
            },
            fh,
            ensure_ascii=False,
            indent=1,
        )
    print(
        f"\n{len(alive)}/{len(rows)} alive ({pct} %) · median {med} ms · "
        f"docs/STATUS.md + docs/status.json written"
    )


if __name__ == "__main__":
    write_status(check_all())
