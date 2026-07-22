#!/usr/bin/env python3
"""Live status of every GTFS feed the backend depends on — run it and see, city
by city, the real HTTP code (200–4xx) for each city's static feed and, where it
has one, its GTFS-Realtime feeds.

    python3 scripts/feeds_status.py

These feeds ARE the only external dependency of the city-transit API (no keys,
no other services). stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "city-transit-api/1.0 (+feeds healthcheck)"}
FLAG = {"PL": "🇵🇱", "DE": "🇩🇪", "US": "🇺🇸", "CZ": "🇨🇿", "SK": "🇸🇰"}


def status(url: str, timeout: int = 30) -> tuple[int, str]:
    """(http_code, note). Try HEAD; fall back to a 1-byte ranged GET for servers
    that reject HEAD. Never downloads the whole (often 10–40 MB) feed."""
    for method, extra in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        req = urllib.request.Request(url, method=method, headers={**UA, **extra})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                size = r.headers.get("Content-Length") or r.headers.get("Content-Range", "").split("/")[-1]
                mb = f"{int(size)/1_000_000:.1f}MB" if size and size.isdigit() else "?"
                return (200 if r.status in (200, 206) else r.status), mb
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 501) and method == "HEAD":
                continue                       # try the ranged GET instead
            return e.code, ""
        except Exception as e:  # noqa: BLE001
            return 0, f"{type(e).__name__}"
    return 0, "unreachable"


def main():
    feeds = json.load(open(os.path.join(ROOT, "feeds.json")))["feeds"]
    print(f"\n  GTFS feed status — {len(feeds)} registered cities  "
          f"({time.strftime('%Y-%m-%d %H:%M')})\n")

    ok = rt = 0
    for f in feeds:
        static_url = f.get("gtfs_static_url")
        flag = FLAG.get(f.get("country", ""), "🏳️")
        if not static_url or not static_url.startswith("http"):
            note = static_url if static_url else "no static URL registered"
            print(f"  ➖  {flag}  {f['id']:18} unverified — {note}")
            continue
        t = time.time()
        code, size = status(static_url)
        ms = int((time.time() - t) * 1000)
        mark = "✅" if code == 200 else ("⚠️" if 400 <= code < 500 else "❌")

        rt_urls = [k for k in ("gtfs_rt_vehicles_url", "gtfs_rt_trips_url", "gtfs_rt_alerts_url") if f.get(k)]
        rt_note = ""
        if rt_urls:
            rc, _ = status(f[rt_urls[0]], timeout=15)
            live = "📡 live" if rc == 200 else f"📡 {rc}"
            rt_note = f"   {live} ({len(rt_urls)} RT)"
            if rc == 200:
                rt += 1

        print(f"  {mark}  {flag}  {f['id']:18} HTTP {code:<3} {ms:>5}ms  {size:>7}   "
              f"{f.get('city_region', '')[:22]:22}{rt_note}")
        if code == 200:
            ok += 1

    print(f"\n  {ok}/{len(feeds)} static feeds answering HTTP 200 · "
          f"{rt} cities with a live GTFS-Realtime feed\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
