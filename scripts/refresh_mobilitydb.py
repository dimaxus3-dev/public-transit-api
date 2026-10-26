#!/usr/bin/env python3
"""Refresh the offline Mobility Database metadata snapshot (stdlib only).

Requires MOBILITY_DB_REFRESH_TOKEN in the process environment. This script
never downloads feed archives or dereferences hosted_url/producer_url.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "feeds_mobilitydb.json"
BASE = "https://api.mobilitydatabase.org"
ENDPOINTS = (
    ("gtfs", "/v1/gtfs_feeds", 500),
    ("gtfs_rt", "/v1/gtfs_rt_feeds", 500),
    ("gbfs", "/v1/gbfs_feeds", 500),
)
SENSITIVE_QUERY_NAMES = {"key", "api_key", "apikey", "token", "access_token", "refresh_token", "authorization"}


class CatalogFailure(Exception):
    """An error whose text contains no URL, response body, or credential."""


class StopOnStatus(CatalogFailure):
    def __init__(self, status: int):
        super().__init__(f"catalog request stopped on HTTP {status}")


class Client:
    def __init__(self, refresh_token: str, *, opener=None, clock=None, sleeper=None):
        self._refresh_token = refresh_token
        self._access_token = None
        self.token_field = None
        self._opener = opener or urllib.request.urlopen
        self._clock = clock or time.monotonic
        self._sleep = sleeper or time.sleep
        self._last_request = None

    def _request(self, path: str, *, method="GET", body=None, authorized=False):
        now = self._clock()
        if self._last_request is not None:
            pause = 1.0 - (now - self._last_request)
            if pause > 0:
                self._sleep(pause)
        self._last_request = self._clock()
        headers = {"Accept": "application/json", "User-Agent": "public-transit-api/catalog-refresh"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if authorized:
            headers["Authorization"] = "Bearer " + self._access_token
        request = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
        try:
            with self._opener(request, timeout=30) as response:
                payload = response.read(32 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429):
                raise StopOnStatus(exc.code) from None
            if exc.code == 401:
                raise CatalogFailure("HTTP 401") from None
            raise CatalogFailure(f"catalog HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise CatalogFailure("catalog network request failed") from None
        if len(payload) > 32 * 1024 * 1024:
            raise CatalogFailure("catalog response exceeded size cap")
        try:
            return json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            raise CatalogFailure("catalog response is not JSON") from None

    def refresh(self):
        body = json.dumps({"refresh_token": self._refresh_token}).encode("utf-8")
        result = self._request("/v1/tokens", method="POST", body=body)
        if not isinstance(result, dict):
            raise CatalogFailure("token response is not an object")
        # Do not assume a particular response field until a real response is seen.
        candidates = [key for key in ("access_token", "token") if isinstance(result.get(key), str) and result[key]]
        if len(candidates) != 1:
            raise CatalogFailure("token response has no unambiguous access-token field")
        self.token_field = candidates[0]
        self._access_token = result[self.token_field]

    def get(self, path: str):
        if self._access_token is None:
            self.refresh()
        try:
            return self._request(path, authorized=True)
        except CatalogFailure as exc:
            if str(exc) != "HTTP 401":
                raise
        self.refresh()
        try:
            return self._request(path, authorized=True)
        except CatalogFailure as exc:
            if str(exc) == "HTTP 401":
                raise CatalogFailure("catalog remained unauthorized after one refresh") from None
            raise


def redact_url(value: str) -> str:
    parts = urllib.parse.urlsplit(value)
    if parts.scheme not in ("http", "https"):
        return value
    pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    if not pairs:
        return value
    safe = [(key, "REDACTED" if key.casefold() in SENSITIVE_QUERY_NAMES else item) for key, item in pairs]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(safe)))


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if key != "hosted_url"}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, str):
        return redact_url(value)
    return value


def collect(client: Client):
    feeds = []
    for data_type, endpoint, limit in ENDPOINTS:
        offset = 0
        while True:
            path = endpoint + "?" + urllib.parse.urlencode({"limit": limit, "offset": offset})
            page = client.get(path)
            if not isinstance(page, list) or any(not isinstance(item, dict) for item in page):
                raise CatalogFailure(f"invalid {data_type} page")
            if any(item.get("data_type") != data_type for item in page):
                raise CatalogFailure(f"unexpected feed type in {data_type} page")
            feeds.extend(clean(page))
            offset += len(page)
            print(f"{data_type}: {offset} metadata records fetched", flush=True)
            if len(page) < limit:
                break
    ids = [feed.get("id") for feed in feeds]
    if any(not isinstance(feed_id, str) for feed_id in ids) or len(set(ids)) != len(ids):
        raise CatalogFailure("catalog contains missing or repeated feed IDs")
    feeds.sort(key=lambda item: (item["data_type"], item["id"]))
    return feeds


def summarize(feeds):
    by_type = Counter(feed["data_type"] for feed in feeds)
    by_status = Counter((feed["data_type"], feed.get("status") or "unknown") for feed in feeds)
    by_country = Counter()
    for feed in feeds:
        countries = {loc.get("country_code") for loc in feed.get("locations") or [] if isinstance(loc, dict)}
        for country in countries or {None}:
            by_country[(feed["data_type"], country or "unknown")] += 1
    auth = Counter(str((feed.get("source_info") or {}).get("authentication_type") or 0) for feed in feeds)
    return {
        "by_type": {key: by_type[key] for key in sorted(by_type)},
        "by_status": {f"{kind}:{status}": count for (kind, status), count in sorted(by_status.items())},
        "by_country": {f"{kind}:{country}": count for (kind, country), count in sorted(by_country.items())},
        "official": sum(feed.get("official") is True for feed in feeds),
        "authentication_type_1": auth["1"],
        "authentication_type_2": auth["2"],
    }


def write_snapshot(path: Path, feeds, *, secrets=()):
    document = {
        "generated_from": "Mobility Database Catalog API",
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "count": len(feeds),
        "summary": summarize(feeds),
        "feeds": feeds,
    }
    encoded = (json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    if any(secret and secret.encode("utf-8") in encoded for secret in secrets):
        raise CatalogFailure("credential found in snapshot; no file written")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".mobilitydb-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return document["summary"]


def main() -> int:
    refresh_token = os.environ.get("MOBILITY_DB_REFRESH_TOKEN", "")
    if not refresh_token:
        print("MOBILITY_DB_REFRESH_TOKEN is absent from the process environment", file=sys.stderr)
        return 2
    client = Client(refresh_token)
    try:
        feeds = collect(client)
        summary = write_snapshot(OUT, feeds, secrets=(refresh_token, client._access_token))
    except CatalogFailure as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"token response field: {client.token_field}")
    print(f"snapshot: {OUT.name}; records: {len(feeds)}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
