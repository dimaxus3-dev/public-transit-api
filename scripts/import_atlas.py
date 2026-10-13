#!/usr/bin/env python3
"""Build ``feeds_atlas.json`` from local Transitland Atlas DMFR data.

The importer is intentionally offline: it only reads JSON files in a local
Atlas checkout and existing registry JSON.  It never fetches feed archives.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT.parent / "sources" / "transitland-atlas" / "feeds"
RT_URL_KINDS = {
    "realtime_alerts": "alerts",
    "realtime_vehicle_positions": "positions",
    "realtime_trip_updates": "trips",
}
KEY_WORDS = {"api_key", "apikey", "key", "token", "access_token", "authorization"}


def normalize_url(value: str) -> str:
    """Normalize only URL components that do not change the requested feed."""
    parts = urlsplit(value.strip())
    netloc = parts.netloc.lower()
    scheme = parts.scheme.lower()
    return urlunsplit((scheme, netloc, parts.path, parts.query, ""))


def host(value: str | None) -> str | None:
    return urlsplit(value).hostname if value else None


def is_direct_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = urlsplit(value.strip())
    return parts.scheme in {"http", "https"} and bool(parts.netloc and parts.path and not parts.path.endswith("/"))


def key_details(feed: dict, url: str | None) -> tuple[bool, str | None]:
    """Return key requirement, preferring DMFR's explicit authorization."""
    authorization = feed.get("authorization")
    if isinstance(authorization, dict):
        return True, authorization.get("info_url") or host(url)
    if url:
        query_names = {part.split("=", 1)[0].lower() for part in urlsplit(url).query.split("&") if part}
        if query_names & KEY_WORDS:
            return True, host(url)
    return False, None


def associated_ids(feed: dict) -> set[str]:
    ids = set()
    for operator in feed.get("operators") or []:
        for association in operator.get("associated_feeds") or []:
            feed_id = association.get("feed_onestop_id")
            if isinstance(feed_id, str):
                ids.add(feed_id)
    return ids


def source_id_to_registry_id(source_id: str) -> str:
    """Return an ASCII path/API-safe slug while retaining ``source_id`` verbatim."""
    candidate = "atlas-" + source_id
    if re.fullmatch(r"[A-Za-z0-9._~-]+", candidate):
        return candidate
    ascii_text = unicodedata.normalize("NFKD", source_id).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9._~-]+", "-", ascii_text).strip("-.") or "feed"
    digest = hashlib.blake2s(source_id.encode("utf-8"), digest_size=6).hexdigest()
    return f"atlas-{stem}-{digest}"


def rt_suffix_kind(feed_id: str) -> str | None:
    tail = feed_id.split("~rt~", 1)
    if len(tail) != 2:
        return None
    return {"alerts": "alerts", "positions": "positions", "trips": "trips"}.get(tail[1])


def collect_rt(static_feed: dict, rt_feeds: list[dict]) -> list[dict]:
    static_id = static_feed["id"]
    linked = associated_ids(static_feed)
    records = []
    for feed in rt_feeds:
        feed_id = feed["id"]
        explicit_link = static_id in associated_ids(feed) or feed_id in linked
        conventional_link = feed_id.startswith(static_id + "~rt")
        if not (explicit_link or conventional_link):
            continue
        suffix_kind = rt_suffix_kind(feed_id)
        for source_key, kind in RT_URL_KINDS.items():
            value = feed.get("urls", {}).get(source_key)
            if not is_direct_url(value):
                continue
            needs_key, provider = key_details(feed, value)
            records.append(
                {
                    "kind": kind,
                    "url": value,
                    "source_feed_id": feed_id,
                    "kind_mismatch": bool(suffix_kind and suffix_kind != kind),
                    "status": "needs_key" if needs_key else "ok",
                    "key_provider": provider,
                }
            )
    return sorted(records, key=lambda row: (row["kind"], row["url"], row["source_feed_id"]))


def agency(feed: dict) -> str | None:
    operators = feed.get("operators") or []
    if operators:
        return operators[0].get("name") or operators[0].get("short_name")
    return None


def build(atlas_feeds: list[dict], world_feeds: list[dict]) -> tuple[list[dict], Counter]:
    """Produce sorted Atlas records and a category summary."""
    world_urls = {normalize_url(f["gtfs_static_url"]) for f in world_feeds if f.get("gtfs_static_url")}
    world_ids = {f.get("id") for f in world_feeds}
    world_agencies = defaultdict(list)
    for f in world_feeds:
        if f.get("country") and f.get("agency_provider"):
            world_agencies[(f["country"], f["agency_provider"].casefold())].append(f["id"])

    static_feeds = [f for f in atlas_feeds if f.get("spec") == "gtfs" and isinstance(f.get("id"), str)]
    rt_feeds = [f for f in atlas_feeds if f.get("spec") == "gtfs-rt" and isinstance(f.get("id"), str)]
    records = []
    summary = Counter()
    for feed in static_feeds:
        static_url = feed.get("urls", {}).get("static_current")
        needs_key, provider = key_details(feed, static_url if isinstance(static_url, str) else None)
        if not is_direct_url(static_url):
            status = "no_direct_url"
            static_url = None
            provider = None
        elif needs_key:
            status = "needs_key"
        else:
            status = "ok"

        source_id = feed["id"]
        registry_id = source_id_to_registry_id(source_id)
        if static_url and normalize_url(static_url) in world_urls:
            summary["duplicate_url"] += 1
            continue
        if source_id in world_ids or registry_id in world_ids:
            summary["duplicate_id"] += 1
            continue

        # DMFR v0.6 has no country field.  It remains null rather than guessed
        # from an ID, hostname, or a decoded geohash.
        country = None
        agency_name = agency(feed)
        possible_ids = world_agencies.get((country, agency_name.casefold()), []) if country and agency_name else []
        record = {
            "id": registry_id,
            "slug": registry_id,
            "source_id": source_id,
            "country": country,
            "city_region": None,
            "agency_provider": agency_name,
            "name": feed.get("name") or agency_name or source_id,
            "gtfs_static_url": static_url,
            "gtfs_rt_urls": collect_rt(feed, rt_feeds),
            "license": copy.deepcopy(feed.get("license")) if "license" in feed else None,
            "attribution": (feed.get("license") or {}).get("attribution_text") or (feed.get("license") or {}).get("attribution_instructions"),
            "source": "transitland-atlas",
            "source_catalog": feed.get("_source_catalog", "feeds"),
            "status": status,
            "key_provider": provider,
            "possible_duplicate": bool(possible_ids),
            "possible_duplicate_ids": sorted(possible_ids),
        }
        records.append(record)
        summary[status] += 1
        summary["rt_endpoints"] += len(record["gtfs_rt_urls"])
        summary["rt_kind_mismatch"] += sum(item["kind_mismatch"] for item in record["gtfs_rt_urls"])

    return sorted(records, key=lambda row: row["id"]), summary


def load_atlas(source: Path) -> list[dict]:
    feeds = []
    for path in sorted(source.glob("*.dmfr.json")):
        with path.open(encoding="utf-8") as fh:
            for feed in json.load(fh).get("feeds", []):
                feed["_source_catalog"] = f"feeds/{path.name}"
                feeds.append(feed)
    return feeds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--world", type=Path, default=ROOT / "feeds_world.json")
    parser.add_argument("--out", type=Path, default=ROOT / "feeds_atlas.json")
    args = parser.parse_args()
    with args.world.open(encoding="utf-8") as fh:
        world = json.load(fh)["feeds"]
    records, summary = build(load_atlas(args.source), world)
    document = {
        "generated_from": "Transitland Atlas DMFR (local checkout)",
        "count": len(records),
        "feeds": records,
    }
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(document, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"wrote {args.out}: {len(records)} records")
    for key in (
        "ok", "needs_key", "no_direct_url", "duplicate_url", "duplicate_id",
        "rt_endpoints", "rt_kind_mismatch",
    ):
        print(f"{key}: {summary[key]}")


if __name__ == "__main__":
    main()
