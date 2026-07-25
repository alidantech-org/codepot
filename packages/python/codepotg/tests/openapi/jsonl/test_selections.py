from __future__ import annotations

import json
from itertools import islice
from pathlib import Path

import pytest

from openapi.jsonl import (
    DEFAULT_SELECTION_CATALOG,
    HotIndexLimits,
    JsonlSelectionError,
    JsonlSelectionStore,
    SelectionCatalog,
    SelectionClass,
    SelectionDefinition,
    SelectionScope,
    compile_openapi_jsonl,
)


def test_selection_catalog_resolves_existing_and_short_names() -> None:
    assert DEFAULT_SELECTION_CATALOG.resolve("schemas.emit_dtos").id == "schemas.emit_dtos"
    assert DEFAULT_SELECTION_CATALOG.resolve("dtos").id == "schemas.emit_dtos"
    assert DEFAULT_SELECTION_CATALOG.resolve("requestBodies").id == (
        "components.request_bodies"
    )


def test_selection_catalog_rejects_duplicate_and_unknown_names() -> None:
    duplicate = SelectionDefinition(
        id="schemas.all",
        selection_class=SelectionClass.SCHEMAS,
        section="components/schemas",
    )
    with pytest.raises(JsonlSelectionError, match="Duplicate selection id"):
        SelectionCatalog((duplicate, duplicate))

    with pytest.raises(JsonlSelectionError, match="Unknown JSONL selection"):
        DEFAULT_SELECTION_CATALOG.resolve("schemas.missing")


def test_jsonl_selection_store_uses_sqlite_handles(tmp_path: Path) -> None:
    cache = _compile_fixture(tmp_path)
    store = JsonlSelectionStore(cache)
    try:
        assert {item.key for item in store.iter_handles("schemas.all")} == {
            "schema:CreateUserDto",
            "schema:Identifier",
            "schema:User",
            "schema:UserStatus",
        }
        assert [item.key for item in store.iter_handles("dtos")] == [
            "schema:CreateUserDto"
        ]
        assert [item.key for item in store.iter_handles("enums")] == [
            "schema:UserStatus"
        ]
        assert [item.key for item in store.iter_handles("operations")] == [
            "operation:get:/users"
        ]
        assert [item.key for item in store.iter_handles("dtos", resource="users")] == [
            "schema:CreateUserDto"
        ]
        assert [
            item.key for item in store.iter_handles("operations", resource="users")
        ] == ["operation:get:/users"]
        assert store.load_count == 0
    finally:
        store.close()


def test_selection_planning_does_not_read_raw_jsonl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = _compile_fixture(tmp_path)
    store = JsonlSelectionStore(cache)
    original = store.index_store.read_location

    def reject_raw_read(*args: object, **kwargs: object) -> object:
        raise AssertionError("Selection planning must not read raw JSONL records")

    try:
        monkeypatch.setattr(store.index_store, "read_location", reject_raw_read)
        schema_handles = tuple(store.iter_handles("schemas.all"))
        operation_groups = tuple(
            store.groups("operations", scope=SelectionScope.RESOURCE)
        )
        assert len(schema_handles) == 4
        assert [(group.resource, group.count) for group in operation_groups] == [
            ("users", 1)
        ]
        assert store.load_count == 0

        monkeypatch.setattr(store.index_store, "read_location", original)
        loaded = store.load(schema_handles[0])
        assert isinstance(loaded.raw, dict)
        assert store.load_count == 1
    finally:
        store.close()


def test_selection_groups_are_lightweight_until_loaded(tmp_path: Path) -> None:
    cache = _compile_fixture(tmp_path)
    store = JsonlSelectionStore(cache)
    try:
        all_groups = tuple(store.groups("schemas.all", scope=SelectionScope.ALL))
        assert len(all_groups) == 1
        assert all_groups[0].count == 4
        assert store.load_count == 0

        resource_groups = tuple(
            store.groups("operations", scope=SelectionScope.RESOURCE)
        )
        assert [(group.resource, group.count) for group in resource_groups] == [
            ("users", 1)
        ]
        assert store.load_count == 0

        dto_handle = next(
            handle
            for handle in all_groups[0].handles
            if handle.key == "schema:CreateUserDto"
        )
        dto = store.load(dto_handle)
        assert dto.raw["x-codegen"]["kind"] == "dto"
        assert store.load_count == 1
    finally:
        store.close()


def test_large_fixture_selection_is_lazy_and_raw_cache_is_bounded(
    tmp_path: Path,
) -> None:
    source = Path(__file__).parents[2] / "fixtures" / "openapi.json"
    result = compile_openapi_jsonl(source, tmp_path / "cache")
    store = JsonlSelectionStore(
        result.cache_dir,
        raw_cache_limits=HotIndexLimits(
            max_entries=1,
            max_bytes=64 * 1024 * 1024,
        ),
    )
    try:
        schema_count = sum(1 for _ in store.iter_handles("schemas.all"))
        assert schema_count == result.manifest.sections["components/schemas"].count
        assert store.load_count == 0

        first_handles = tuple(islice(store.iter_handles("schemas.all"), 3))
        assert len(first_handles) == 3
        for handle in first_handles:
            store.load(handle)

        stats = store.raw_cache_stats()
        assert stats.entries <= 1
        assert stats.evictions >= 2
        assert store.load_count == 3

        operation_handles = tuple(store.iter_handles("operations"))
        assert operation_handles
        assert all(handle.key.startswith("operation:") for handle in operation_handles)
    finally:
        store.close()


def _compile_fixture(tmp_path: Path) -> Path:
    source = tmp_path / "openapi.json"
    source.write_text(json.dumps(_document()), encoding="utf-8")
    cache = tmp_path / "cache"
    compile_openapi_jsonl(source, cache)
    return cache


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Selection API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "x-codegen": {"resource": {"name": "users"}},
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/User"},
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "x-codegen": {"kind": "model", "resource": "users"},
                    "properties": {"id": {"$ref": "#/components/schemas/Identifier"}},
                },
                "CreateUserDto": {
                    "type": "object",
                    "x-codegen": {"kind": "dto", "resource": "users"},
                    "properties": {"name": {"type": "string"}},
                },
                "UserStatus": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "x-codegen": {"resource": "users"},
                },
                "Identifier": {"type": "string"},
            },
            "responses": {
                "ListUsersResponse": {
                    "description": "OK",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    },
                }
            },
        },
        "x-codegen": {
            "resources": {"users": {"name": "users"}},
            "entities": {"UserEntity": {"resource": "users"}},
            "access": {"users.read": {"resource": "users"}},
            "frontends": {"admin": {"resources": ["users"]}},
        },
    }
