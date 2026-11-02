import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "import_atlas.py"
SPEC = importlib.util.spec_from_file_location("import_atlas", MODULE_PATH)
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def test_build_preserves_license_marks_key_and_rt_mismatch():
    static = {
        "id": "f-demo",
        "spec": "gtfs",
        "urls": {"static_current": "https://example.test/feed.zip"},
        "license": {"spdx_identifier": "CC-BY-4.0", "redistribution_allowed": "yes"},
        "operators": [{"name": "Demo Transit", "associated_feeds": [{"feed_onestop_id": "f-demo~rt~alerts"}]}],
    }
    realtime = {
        "id": "f-demo~rt~alerts",
        "spec": "gtfs-rt",
        "urls": {"realtime_vehicle_positions": "https://example.test/live.pb"},
        "authorization": {"type": "query_param", "info_url": "https://keys.example.test"},
    }
    records, summary = IMPORTER.build([static, realtime], [])
    record = records[0]
    assert record["id"] == "atlas-f-demo"
    assert record["license"] == static["license"]
    assert record["status"] == "ok"
    assert record["country"] is None
    assert record["gtfs_rt_urls"] == [{
        "kind": "positions", "url": "https://example.test/live.pb",
        "source_feed_id": "f-demo~rt~alerts", "kind_mismatch": True,
        "status": "needs_key", "key_provider": "https://keys.example.test",
    }]
    assert summary["rt_kind_mismatch"] == 1


def test_build_marks_missing_direct_url_and_heuristic_key():
    no_url = {"id": "f-none", "spec": "gtfs", "urls": {"static_current": "https://example.test/"}}
    keyed = {"id": "f-key", "spec": "gtfs", "urls": {"static_current": "https://feeds.test/a.zip?api_key=redacted"}}
    records, _ = IMPORTER.build([no_url, keyed], [])
    assert records[0]["status"] == "needs_key"
    assert records[0]["key_provider"] == "feeds.test"
    assert records[1]["status"] == "no_direct_url"
    assert records[1]["gtfs_static_url"] is None


def test_deduplicates_url_and_is_idempotent(tmp_path):
    atlas = {"id": "f-demo", "spec": "gtfs", "urls": {"static_current": "HTTPS://EXAMPLE.TEST/a.zip#ignored"}}
    world = [{"id": "mdb-1", "gtfs_static_url": "https://example.test/a.zip"}]
    assert IMPORTER.build([atlas], world)[0] == []
    source = tmp_path / "feeds"
    source.mkdir()
    (source / "demo.dmfr.json").write_text(json.dumps({"feeds": [atlas]}))
    loaded = IMPORTER.load_atlas(source)
    assert loaded[0]["id"] == atlas["id"]
    assert loaded[0]["_source_catalog"] == "feeds/demo.dmfr.json"


def test_non_ascii_source_id_gets_a_portable_slug():
    slug = IMPORTER.source_id_to_registry_id("f-aléop~市")
    assert slug.startswith("atlas-f-aleop~")
    assert slug.isascii()
    assert all(character.isalnum() or character in "._~-" for character in slug)
