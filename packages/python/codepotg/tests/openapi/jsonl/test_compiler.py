from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from openapi.jsonl import HotIndexLimits, JsonlIndexStore, compile_openapi_jsonl

_HTTP_METHODS = frozenset(
    {"get", "put", "post", "delete", "patch", "options", "head", "trace"}
)
_COMPONENT_COLLECTIONS = frozenset(
    {
        "schemas",
        "parameters",
        "requestBodies",
        "responses",
        "securitySchemes",
        "headers",
        "examples",
        "links",
        "callbacks",
        "pathItems",
    }
)
_X_CODEGEN_COLLECTIONS = frozenset(
    {"resources", "frontends", "access", "baseEntities", "entities"}
)


@dataclass(frozen=True)
class ProjectFixture:
    relative: str


@dataclass(frozen=True)
class FixtureExpectation:
    paths: int
    schemas: int
    records: int
    schema_name: str
    schema: Mapping[str, Any]
    method: str
    operation_id: str
    operation_path: str
    resource: str
    dependency_ref: str


PROJECT_FIXTURES = (
    ProjectFixture(relative="projects/typescript/openapi.json"),
    ProjectFixture(relative="projects/dart/openapi.json"),
)


@pytest.mark.parametrize("fixture", PROJECT_FIXTURES)
def test_large_project_fixture_streams_to_indexed_jsonl(
    fixture: ProjectFixture,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Path(__file__).parents[2] / "fixtures" / fixture.relative
    assert source.stat().st_size > 1_000_000
    expectation = _inspect_fixture(source)

    def reject_full_document_load(*args: object, **kwargs: object) -> object:
        raise AssertionError("JSONL compiler must not call json.load()")

    monkeypatch.setattr(json, "load", reject_full_document_load)
    result = compile_openapi_jsonl(
        source,
        tmp_path / "cache",
        hot_limits=HotIndexLimits(max_entries=8, max_bytes=8 * 1024),
    )

    assert not result.reused
    assert result.records_written == expectation.records
    assert result.manifest.sections["paths"].count == expectation.paths
    assert result.manifest.sections["components/schemas"].count == expectation.schemas
    assert result.manifest.sections["paths"].file == "paths.jsonl"
    assert result.manifest.sections["components/schemas"].file == (
        "components/schemas.jsonl"
    )

    hot_stats = result.hot_index.stats()
    assert hot_stats.entries <= 8
    assert hot_stats.estimated_bytes <= 8 * 1024
    assert hot_stats.evictions > 0

    store = JsonlIndexStore(result.cache_dir, hot_index=result.hot_index)

    schema_ref = f"#/components/schemas/{expectation.schema_name}"
    schema_location = store.get_by_ref(schema_ref)
    assert schema_location is not None
    assert schema_location.file == "components/schemas.jsonl"
    assert store.read_location(schema_location) == expectation.schema

    operation_key = (
        f"operation:{expectation.method}:{expectation.operation_path}"
    )
    operation_location = store.get_by_operation_id(expectation.operation_id)
    assert operation_location is not None
    assert operation_location.key == operation_key
    operation = store.read_location(operation_location)
    assert operation["operationId"] == expectation.operation_id

    resource_mentions = store.find_mentions("resource", expectation.resource)
    assert resource_mentions
    assert any(fact["item"] == operation_key for fact in resource_mentions)

    operation_kind_mentions = store.find_mentions("kind", "operation")
    assert any(fact["item"] == operation_key for fact in operation_kind_mentions)

    dependants = store.find_dependants(expectation.dependency_ref)
    assert any(fact["from"] == operation_key for fact in dependants)
    assert all(fact["to"] == expectation.dependency_ref for fact in dependants)


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


def _inspect_fixture(source: Path) -> FixtureExpectation:
    document = json.loads(source.read_text(encoding="utf-8"))
    paths = _mapping(document.get("paths"), "paths")
    components = _mapping(document.get("components", {}), "components")
    codegen = _mapping(document.get("x-codegen", {}), "x-codegen")
    schemas = _mapping(components.get("schemas"), "components.schemas")

    records = len(paths)
    records += sum(
        len(_mapping(components.get(collection, {}), f"components.{collection}"))
        for collection in _COMPONENT_COLLECTIONS
    )
    records += sum(
        len(_mapping(codegen.get(collection, {}), f"x-codegen.{collection}"))
        for collection in _X_CODEGEN_COLLECTIONS
    )

    schema_name, schema = next(iter(schemas.items()))
    if not isinstance(schema, Mapping):
        raise AssertionError(f"Fixture schema {schema_name!r} must be an object")

    operation_path, method, operation, resource, dependency_ref = _find_operation(paths)
    operation_id = operation.get("operationId")
    if not isinstance(operation_id, str) or not operation_id:
        raise AssertionError("Selected fixture operation must have an operationId")

    return FixtureExpectation(
        paths=len(paths),
        schemas=len(schemas),
        records=records,
        schema_name=str(schema_name),
        schema=schema,
        method=method,
        operation_id=operation_id,
        operation_path=operation_path,
        resource=resource,
        dependency_ref=dependency_ref,
    )


def _find_operation(
    paths: Mapping[str, Any],
) -> tuple[str, str, Mapping[str, Any], str, str]:
    for path, path_item_value in paths.items():
        if not isinstance(path_item_value, Mapping):
            continue
        path_resource = _resource_name(path_item_value)
        for method, operation_value in path_item_value.items():
            lowered = str(method).lower()
            if lowered not in _HTTP_METHODS or not isinstance(operation_value, Mapping):
                continue
            operation_id = operation_value.get("operationId")
            resource = _resource_name(operation_value) or path_resource
            dependency_ref = next(_refs(operation_value), None)
            if isinstance(operation_id, str) and operation_id and resource and dependency_ref:
                return str(path), lowered, operation_value, resource, dependency_ref
    raise AssertionError("Fixture must contain an indexed operation, resource, and dependency ref")


def _resource_name(value: Mapping[str, Any]) -> str | None:
    codegen = value.get("x-codegen")
    if not isinstance(codegen, Mapping):
        return None
    resource = codegen.get("resource")
    if isinstance(resource, str) and resource:
        return resource
    if not isinstance(resource, Mapping):
        return None
    name = resource.get("name")
    if isinstance(name, str) and name:
        return name
    ref = resource.get("$ref")
    prefix = "#/x-codegen/resources/"
    if isinstance(ref, str) and ref.startswith(prefix):
        return ref[len(prefix) :].split("/", 1)[0]
    return None


def _refs(value: Any) -> Iterator[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                yield child
            else:
                yield from _refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _refs(child)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"Fixture {name} must be an object")
    return value


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
