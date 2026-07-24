"""Transit Intelligence — aggregated analytics behind the /dashboard module.

Merges every real signal the platform already produces into one compact
payload the dashboard renders client-side:

    docs/status.json       availability of all feeds (HTTP, latency, size)
    docs/deep_check.json   end-to-end funnel (reachable → ingested → routable)
    data/<id>/summary.json ingested network sizes (routes/stops/trips)
    feeds_gbfs.json        shared-mobility systems per country
    feeds.json             curated realtime (GTFS-RT) coverage

Also computes the proprietary per-country **Coverage Score (0-100)**:

    35 %  availability      (alive feeds / feeds)
    25 %  ingestability     (deep-check: valid GTFS end-to-end)
    15 %  routability       (deep-check: CSA planned a trip today)
    10 %  latency           (median response, 200 ms → 1000 ms window)
    10 %  shared mobility   (GBFS systems present)
     5 %  realtime          (curated GTFS-RT feeds present)

Tiers: ≥85 Excellent · ≥70 Good · ≥50 Average · ≥30 Poor · else Critical.
Everything is cached in-process and recomputed only when a source file's
mtime changes. stdlib only.
"""

from __future__ import annotations

import json
import os
import statistics
import threading
import time

from . import registry, store
from .paths import DATA_DIR, registry_file

_DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

_lock = threading.Lock()
_cache: dict = {"stamp": None, "payload": None}

_WEIGHTS = {"alive": 35, "ingested": 25, "routable": 15, "latency": 10, "gbfs": 10, "rt": 5}
_TIERS = [(85, "Excellent"), (70, "Good"), (50, "Average"), (30, "Poor"), (0, "Critical")]


def _read_json(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001 — a missing report just means fewer panels
        return None


def _sources() -> dict:
    return {
        "status": os.path.join(_DOCS, "status.json"),
        "deep": os.path.join(_DOCS, "deep_check.json"),
        "gbfs": registry_file("feeds_gbfs.json"),
        "curated": registry_file("feeds.json"),
    }


def _stamp() -> tuple:
    parts = []
    for p in _sources().values():
        try:
            parts.append(os.path.getmtime(p))
        except OSError:
            parts.append(0)
    parts.append(tuple(sorted(store.available_feeds())))
    return tuple(parts)


def tier(score: float) -> str:
    for floor, name in _TIERS:
        if score >= floor:
            return name
    return "Critical"


def _latency_score(median_ms: float) -> float:
    """1.0 at ≤200 ms, linear to 0.0 at ≥1000 ms."""
    if median_ms <= 0:
        return 0.0
    return max(0.0, min(1.0, (1000 - median_ms) / 800))


def build() -> dict:
    """The full intelligence payload (cached until a source file changes)."""
    stamp = _stamp()
    with _lock:
        if _cache["stamp"] == stamp and _cache["payload"]:
            return _cache["payload"]

    src = _sources()
    status = _read_json(src["status"]) or {"feeds": [], "median_ms": 0, "checked_at": None}
    deep = _read_json(src["deep"]) or {"results": []}
    gbfs_reg = _read_json(src["gbfs"]) or {"systems": []}
    curated = (_read_json(src["curated"]) or {}).get("feeds", [])

    # ── per-country aggregation ──────────────────────────────────────────────
    countries: dict[str, dict] = {}

    def C(cc: str) -> dict:
        cc = (cc or "?").strip().upper() or "?"
        return countries.setdefault(
            cc,
            {
                "country": cc,
                "feeds": 0,
                "alive": 0,
                "latencies": [],
                "deep_n": 0,
                "deep_ingested": 0,
                "deep_routable": 0,
                "gbfs": 0,
                "rt": 0,
                "cities": set(),
            },
        )

    for f in status["feeds"]:
        c = C(f.get("country"))
        c["feeds"] += 1
        c["alive"] += 1 if f.get("ok") else 0
        if f.get("ok") and f.get("ms"):
            c["latencies"].append(f["ms"])
        if f.get("city"):
            c["cities"].add(f["city"])

    for r in deep.get("results", []):
        c = C(r.get("country"))
        c["deep_n"] += 1
        c["deep_ingested"] += 1 if r.get("ingested") else 0
        c["deep_routable"] += 1 if r.get("routable") else 0

    for s in gbfs_reg.get("systems", []):
        C(s.get("country"))["gbfs"] += 1

    for f in curated:
        if f.get("gtfs_rt_vehicles_url") or f.get("gtfs_rt_trips_url"):
            C(f.get("country"))["rt"] += 1

    out_countries = []
    for cc, c in countries.items():
        if cc == "?":
            continue
        alive_r = c["alive"] / c["feeds"] if c["feeds"] else 0.0
        ing_r = c["deep_ingested"] / c["deep_n"] if c["deep_n"] else alive_r
        route_r = c["deep_routable"] / c["deep_n"] if c["deep_n"] else 0.0
        med = statistics.median(c["latencies"]) if c["latencies"] else 0
        score = (
            _WEIGHTS["alive"] * alive_r
            + _WEIGHTS["ingested"] * ing_r
            + _WEIGHTS["routable"] * route_r
            + _WEIGHTS["latency"] * _latency_score(med)
            + _WEIGHTS["gbfs"] * (1.0 if c["gbfs"] else 0.0)
            + _WEIGHTS["rt"] * (1.0 if c["rt"] else 0.0)
        )
        # Coverage tier for the map
        if c["feeds"] == 0 and c["gbfs"] == 0:
            cov = "none"
        elif alive_r < 0.3:
            cov = "down"
        elif c["rt"] and c["gbfs"]:
            cov = "premium"  # transit + realtime + shared mobility
        elif c["rt"]:
            cov = "realtime"
        elif score >= 80:
            cov = "full"
        else:
            cov = "partial"
        out_countries.append(
            {
                "country": cc,
                "feeds": c["feeds"],
                "alive": c["alive"],
                "cities": len(c["cities"]),
                "median_ms": int(med),
                "deep_checked": c["deep_n"],
                "ingested": c["deep_ingested"],
                "routable": c["deep_routable"],
                "gbfs_systems": c["gbfs"],
                "realtime_feeds": c["rt"],
                "score": round(score, 1),
                "tier": tier(score),
                "coverage": cov,
            }
        )
    out_countries.sort(key=lambda x: -x["score"])

    # ── ingested-network stats ───────────────────────────────────────────────
    feeds_meta = registry.load()
    cities = []
    totals = {"routes": 0, "stops": 0, "trips": 0, "shapes": 0}
    for fid in store.available_feeds():
        s = _read_json(os.path.join(DATA_DIR, fid, "summary.json"))
        if not s:
            continue
        m = feeds_meta.get(fid, {})
        cities.append(
            {
                "feed": fid,
                "city": m.get("city_region", fid),
                "country": m.get("country"),
                "routes": s.get("routes", 0),
                "stops": s.get("stops", 0),
                "trips": s.get("trips", 0),
                "timezone": s.get("timezone"),
            }
        )
        for k in totals:
            totals[k] += s.get(k, 0)
    cities.sort(key=lambda x: -x["stops"])

    # ── data quality (from the deep-check failure notes) ─────────────────────
    fail_kinds: dict[str, int] = {}
    for r in deep.get("results", []):
        if r.get("routable"):
            continue
        note = (r.get("note") or "").lower()
        if not r.get("reachable"):
            kind = "unreachable"
        elif not r.get("ingested"):
            if "zip" in note or "gtfs" in note:
                kind = "invalid archive / not GTFS"
            elif "exceed" in note or "limit" in note:
                kind = "over resource limits"
            elif "timeout" in note or "exceeded" in note:
                kind = "ingest timeout"
            else:
                kind = "ingest error"
        elif "no service" in note or "calendar" in note:
            kind = "expired calendar"
        elif "no multi-stop" in note or "stops unresolved" in note:
            kind = "degenerate trips"
        elif note.startswith("skipped"):
            kind = "skipped (size cap)"
        else:
            kind = "router found no trip"
        fail_kinds[kind] = fail_kinds.get(kind, 0) + 1

    n_total = len(status["feeds"]) or 1
    alive_total = sum(1 for f in status["feeds"] if f.get("ok"))
    deep_res = deep.get("results", [])
    dq = {
        "freshness": round(100 * alive_total / n_total, 1),
        "completeness": round(
            100 * sum(1 for r in deep_res if r.get("ingested")) / (len(deep_res) or 1), 1
        ),
        "integrity": round(
            100 * sum(1 for r in deep_res if r.get("routable")) / (len(deep_res) or 1), 1
        ),
        "issues": sorted(fail_kinds.items(), key=lambda kv: -kv[1]),
    }
    dq["overall"] = round((dq["freshness"] + dq["completeness"] + dq["integrity"]) / 3, 1)

    # ── latency histogram for the health panel ───────────────────────────────
    buckets = [0] * 10  # 0-100, …, 900+ ms
    for f in status["feeds"]:
        if f.get("ok") and f.get("ms") is not None:
            buckets[min(9, int(f["ms"] // 100))] += 1

    world_scores = [c["score"] for c in out_countries]
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checked_at": status.get("checked_at"),
        "kpi": {
            "countries": len(out_countries),
            "feeds": len(status["feeds"]),
            "alive": alive_total,
            "cities_ingested": len(cities),
            "routes": totals["routes"],
            "stops": totals["stops"],
            "trips": totals["trips"],
            "gbfs_systems": len(gbfs_reg.get("systems", [])),
            "gbfs_countries": len({s.get("country") for s in gbfs_reg.get("systems", [])}),
            "realtime_feeds": sum(c["realtime_feeds"] for c in out_countries),
            "median_ms": status.get("median_ms", 0),
            "deep": {
                "checked": len(deep_res),
                "reachable": sum(1 for r in deep_res if r.get("reachable")),
                "ingested": sum(1 for r in deep_res if r.get("ingested")),
                "routable": sum(1 for r in deep_res if r.get("routable")),
            },
            "coverage_score": round(statistics.mean(world_scores), 1) if world_scores else 0,
            "quality": dq["overall"],
        },
        "countries": out_countries,
        "cities": cities,
        "quality": dq,
        "latency_histogram": buckets,
        "score_model": {"weights": _WEIGHTS, "tiers": [t for _, t in _TIERS]},
    }
    with _lock:
        _cache["stamp"] = stamp
        _cache["payload"] = payload
    return payload
