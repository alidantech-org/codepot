from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from openapi.jsonl import HotIndexLimits, JsonlIndexStore, compile_openapi_jsonl


@dataclass(frozen=True)
class ProjectFixture:
    relative: str
    paths: int
    schemas: int
    records: int
    operation_id: str
    operation_path: str
    resource: str


PROJECT_FIXTURES = (
    ProjectFixture(
        relative="projects/typescript/openapi.json",
        paths=108,
        schemas=530,
        records=1142,
        operation_id="findApps",
        operation_path="/platform/apps",
        resource="apps",
    ),
    ProjectFixture(
        relative="projects/dart/openapi.json",
        paths=227,
        schemas=1268,
        records=2429,
        operation_id="getHello",
        operation_path="/",
        resource="application",
    ),
)


@pytest.mark.parametrize("fixture", PROJECT_FIXTURES)
def test_large_project_fixture_streams_to_indexed_jsonl(
    fixture: ProjectFixture,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Path(__file__).parents[2] / "fixtures" / fixture.relative
    assert source.stat().st_size > 1_000_000

    def reject_full_document_load(*args: object, **kwargs: object) -> object:
        raise AssertionError("JSONL compiler must not call json.load()")

    monkeypatch.setattr(json, "load", reject_full_document_load)
    result = compile_openapi_jsonl(
        source,
        tmp_path / "cache",
        hot_limits=HotIndexLimits(max_entries=8, max_bytes=8 * 1024),
    )

    assert not result.reused
    assert result.records_written == fixture.records
    assert result.manifest.sections["paths"].count == fixture.paths
    assert result.manifest.sections["components/schemas"].count == fixture.schemas
    assert result.manifest.sections["paths"].file == "paths.jsonl"
    assert result.manifest.sections["components/schemas"].file == (
        "components/schemas.jsonl"
    )

    hot_stats = result.hot_index.stats()
    assert hot_stats.entries <= 8
    assert hot_stats.estimated_bytes <= 8 * 1024
    assert hot_stats.evictions > 0

    store = JsonlIndexStore(result.cache_dir, hot_index=result.hot_index)

    # SharedUuid is near the beginning of both fixtures and should be evicted.
    schema_location = store.get_by_ref("#/components/schemas/SharedUuid")
    assert schema_location is not None
    assert schema_location.file == "components/schemas.jsonl"
    assert store.read_location(schema_location)["type"] == "string"

    operation_location = store.get_by_operation_id(fixture.operation_id)
    assert operation_location is not None
    assert operation_location.key == f"operation:get:{fixture.operation_path}"
    operation = store.read_location(operation_location)
    assert operation["operationId"] == fixture.operation_id

    resource_mentions = store.find_mentions("resource", fixture.resource)
    assert resource_mentions
    assert any(
        fact["item"].startswith(("schema:", "resource:"))
        for fact in resource_mentions
    )

    dependants = store.find_dependants("#/components/schemas/SharedUuid")
    assert dependants
    assert all(
        fact["to"] == "#/components/schemas/SharedUuid" for fact in dependants
    )


@pytest.mark.parametrize("fixture", PROJECT_FIXTURES)
def test_jsonl_output_is_deterministic_and_reuses_unchanged_source(
    fixture: ProjectFixture,
    tmp_path: Path,
) -> None:
    source = Path(__file__).parents[2] / "fixtures" / fixture.relative
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = compile_openapi_jsonl(source, first_dir)
    second = compile_openapi_jsonl(source, second_dir)

    assert first.manifest.to_json() == second.manifest.to_json()
    assert _tree_hashes(first_dir) == _tree_hashes(second_dir)

    reused = compile_openapi_jsonl(source, first_dir)
    assert reused.reused
    assert reused.records_written == 0
    assert reused.manifest.to_json() == first.manifest.to_json()


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
