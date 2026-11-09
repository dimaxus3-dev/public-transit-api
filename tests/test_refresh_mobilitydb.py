import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest


PATH = Path(__file__).parents[1] / "scripts" / "refresh_mobilitydb.py"
SPEC = importlib.util.spec_from_file_location("refresh_mobilitydb", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Response:
    def __init__(self, value):
        self.value = json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _):
        return self.value


def test_pagination_401_refresh_and_summary():
    calls = []
    results = [
        {"access_token": "fixture-access-1"},
        urllib.error.HTTPError("https://example.test", 401, "unauthorized", {}, None),
        {"access_token": "fixture-access-2"},
        [{"id": "mdb-1", "data_type": "gtfs", "official": True, "status": "active",
          "locations": [{"country_code": "CA"}], "source_info": {"authentication_type": 1},
          "latest_dataset": {"hosted_url": "https://example.test/archive.zip"}}],
        [],
        [],
    ]

    def opener(request, timeout):
        calls.append((request.full_url, request.get_method()))
        result = results.pop(0)
        if isinstance(result, Exception):
            raise result
        return Response(result)

    client = MODULE.Client("fixture-refresh", opener=opener, clock=lambda: 0, sleeper=lambda _: None)
    feeds = MODULE.collect(client)
    assert len(feeds) == 1
    assert "hosted_url" not in feeds[0]["latest_dataset"]
    assert calls[0][1] == "POST"
    assert len([method for _, method in calls if method == "POST"]) == 2
    assert MODULE.summarize(feeds)["authentication_type_1"] == 1
    assert MODULE.summarize(feeds)["by_country"] == {"gtfs:CA": 1}


@pytest.mark.parametrize("status", [403, 429])
def test_stop_status_does_not_expose_response_or_credential(status):
    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, status, "fixture-secret", {}, io.BytesIO(b"fixture-secret"))

    client = MODULE.Client("fixture-secret", opener=opener, clock=lambda: 0, sleeper=lambda _: None)
    with pytest.raises(MODULE.StopOnStatus) as raised:
        client.refresh()
    assert str(status) in str(raised.value)
    assert "fixture-secret" not in str(raised.value)


def test_snapshot_redacts_key_query_and_credential(tmp_path):
    feed = {"id": "mdb-1", "data_type": "gtfs", "source_info": {
        "producer_url": "https://example.test/feed?api_key=fixture-secret&kind=gtfs"}}
    cleaned = MODULE.clean(feed)
    assert "fixture-secret" not in json.dumps(cleaned)
    target = tmp_path / "snapshot.json"
    MODULE.write_snapshot(target, [cleaned], secrets=("fixture-secret",))
    assert target.exists()
    with pytest.raises(MODULE.CatalogFailure):
        MODULE.write_snapshot(target, [feed], secrets=("fixture-secret",))
