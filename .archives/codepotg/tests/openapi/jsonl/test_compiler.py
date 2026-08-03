from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from openapi.jsonl import (
    HotIndexLimits,
    JsonlIndexStore,
    JsonlQueueLimits,
    compile_openapi_jsonl,
)


def test_large_real_fixture_streams_to_sqlite_indexed_jsonl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _real_fixture()
    assert source.stat().st_size > 1_000_000

    def reject_full_document_load(*args: object, **kwargs: object) -> object:
        raise AssertionError("JSONL compiler must not call json.load()")

    monkeypatch.setattr(json, "load", reject_full_document_load)
    result = compile_openapi_jsonl(
        source,
        tmp_path / "cache",
        hot_limits=HotIndexLimits(max_entries=8, max_bytes=8 * 1024),
        queue_limits=JsonlQueueLimits(
            max_records=2,
            max_pending_bytes=32 * 1024 * 1024,
            max_events=2,
        ),
    )

    assert not result.reused
    assert result.records_written > 100
    assert result.manifest.sections["paths"].count > 10
    assert result.manifest.sections["components/schemas"].count > 100
    assert result.manifest.sections["paths"].file == "paths.jsonl"
    assert result.manifest.sections["components/schemas"].file == (
        "components/schemas.jsonl"
    )
    assert (result.cache_dir / "index.sqlite").is_file()
    assert {
        value["backend"] for value in result.manifest.indexes.values()
    } == {"sqlite"}
    assert {
        value["database"] for value in result.manifest.indexes.values()
    } == {"index.sqlite"}

    hot_stats = result.hot_index.stats()
    assert hot_stats.entries <= 8
    assert hot_stats.estimated_bytes <= 8 * 1024
    assert hot_stats.evictions > 0

    queue_stats = result.queue_stats
    assert 1 <= queue_stats.record_high_water <= 2
    assert 1 <= queue_stats.event_high_water <= 2
    assert 1 <= queue_stats.pending_bytes_high_water <= 32 * 1024 * 1024

    events_manifest = result.manifest.events
    assert events_manifest is not None
    assert events_manifest.file == "events.jsonl"
    assert events_manifest.count == 2
    events = [
        json.loads(line)
        for line in (result.cache_dir / events_manifest.file).read_text().splitlines()
    ]
    assert events == [
        {"sequence": 1, "stage": "compiler", "status": "started"},
        {"sequence": 2, "stage": "compiler", "status": "completed"},
    ]

    # The monkeypatch proves the compiler itself never used json.load(). Restore it
    # before constructing the ordinary cache reader, which may inspect the manifest.
    monkeypatch.undo()
    store = JsonlIndexStore(result.cache_dir, hot_index=result.hot_index)
    try:
        schema_ref = "#/components/schemas/AppStatus"
        schema_location = store.get_by_ref(schema_ref)
        assert schema_location is not None
        assert schema_location.file == "components/schemas.jsonl"
        assert store.read_location(schema_location)["enum"] == [
            "active",
            "suspended",
            "disabled",
        ]

        operation_key = "operation:get:/platform/apps"
        operation_location = store.get_by_operation_id("findApps")
        assert operation_location is not None
        assert operation_location.key == operation_key
        operation = store.read_location(operation_location)
        assert operation["operationId"] == "findApps"

        resource_mentions = store.find_mentions("resource", "apps")
        assert resource_mentions
        assert any(fact["item"] == operation_key for fact in resource_mentions)

        operation_kind_mentions = store.find_mentions("kind", "operation")
        assert any(fact["item"] == operation_key for fact in operation_kind_mentions)

        dependency_ref = "#/components/schemas/AppListQuery"
        dependants = store.find_dependants(dependency_ref)
        assert any(fact["from"] == operation_key for fact in dependants)
        assert all(fact["to"] == dependency_ref for fact in dependants)
    finally:
        store.close()


def test_jsonl_output_is_deterministic_and_reuses_unchanged_source(
    tmp_path: Path,
) -> None:
    source = _real_fixture()
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = compile_openapi_jsonl(source, first_dir)
    second = compile_openapi_jsonl(source, second_dir)

    assert first.manifest.to_json() == second.manifest.to_json()
    assert _tree_hashes(first_dir) == _tree_hashes(second_dir)
    assert _sqlite_signature(first_dir) == _sqlite_signature(second_dir)

    reused = compile_openapi_jsonl(source, first_dir)
    assert reused.reused
    assert reused.records_written == 0
    assert reused.manifest.to_json() == first.manifest.to_json()


def _real_fixture() -> Path:
    return Path(__file__).parents[2] / "fixtures" / "openapi.json"


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "index.sqlite"
    }


def _sqlite_signature(root: Path) -> tuple[tuple[object, ...], ...]:
    connection = sqlite3.connect(root / "index.sqlite")
    try:
        rows: list[tuple[object, ...]] = []
        for table, order_by in (
            ("locations", "key"),
            ("definitions", "lookup, value"),
            ("mentions", "index_name, value, item, purpose, file"),
            ("dependencies", "source, target, purpose, file"),
        ):
            rows.extend(
                (table, *row)
                for row in connection.execute(
                    f"SELECT * FROM {table} ORDER BY {order_by}"  # noqa: S608
                )
            )
        return tuple(rows)
    finally:
        connection.close()
