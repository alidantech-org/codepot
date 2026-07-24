from __future__ import annotations

import json
from pathlib import Path

import pytest

from openapi.jsonl import (
    JsonlLazyResolver,
    JsonlLookupError,
    LazyResolverLimits,
    compile_openapi_jsonl,
)


def test_lazy_record_stays_cold_until_mapping_access(tmp_path: Path) -> None:
    cache = _compile(tmp_path)
    resolver = JsonlLazyResolver(cache)

    user = resolver.ref("#/components/schemas/User")

    assert user is not None
    assert not user.loaded
    assert resolver.load_count == 0
    assert user.key == "schema:User"
    assert user.kind == "model"
    assert user.resources == ("users",)
    assert not user.loaded

    assert user["type"] == "object"
    assert user.loaded
    assert resolver.load_count == 1
    assert user.get("missing", "fallback") == "fallback"

    same = resolver.ref("#/components/schemas/User")
    assert same is user
    assert same["type"] == "object"
    assert resolver.load_count == 1


def test_lazy_operation_resource_and_dependant_resolution(tmp_path: Path) -> None:
    cache = _compile(tmp_path)
    resolver = JsonlLazyResolver(cache)

    operation = resolver.operation("listUsers")
    assert operation is not None
    assert operation.key == "operation:get:/users"
    assert not operation.loaded
    assert operation["operationId"] == "listUsers"

    resource_records = resolver.resource("users")
    assert {item.key for item in resource_records} >= {
        "schema:User",
        "schema:UserStatus",
        "operation:get:/users",
    }
    assert all(not item.loaded for item in resource_records if item is not operation)

    dependants = resolver.dependants("#/components/schemas/UserStatus")
    assert {item.key for item in dependants} == {"schema:User"}
    assert all(not item.loaded for item in dependants)


def test_lazy_proxy_cache_evicts_by_entry_limit_and_reloads(tmp_path: Path) -> None:
    cache = _compile(tmp_path)
    resolver = JsonlLazyResolver(
        cache,
        limits=LazyResolverLimits(cache_entries=1, cache_bytes=1024 * 1024),
    )

    user = resolver.ref("#/components/schemas/User")
    status = resolver.ref("#/components/schemas/UserStatus")

    assert user is not None
    assert status is not None
    stats = resolver.stats()["proxyCache"]
    assert stats.entries <= 1
    assert stats.evictions >= 1

    user_again = resolver.ref("#/components/schemas/User")
    assert user_again is not None
    assert user_again is not user
    assert user_again["type"] == "object"
    assert resolver.load_count == 1


def test_lazy_resolver_enforces_depth_and_record_byte_limits(tmp_path: Path) -> None:
    cache = _compile(tmp_path)
    resolver = JsonlLazyResolver(
        cache,
        limits=LazyResolverLimits(max_depth=1, max_record_bytes=1),
    )

    with pytest.raises(JsonlLookupError, match="depth 2 exceeds limit 1"):
        resolver.chain("#/components/schemas/UserStatus", depth=2)

    with pytest.raises(JsonlLookupError, match="exceeds lazy resolver byte limit"):
        resolver.ref("#/components/schemas/User")


def _compile(tmp_path: Path) -> Path:
    source = tmp_path / "openapi.json"
    source.write_text(json.dumps(_document()), encoding="utf-8")
    cache = tmp_path / "cache"
    compile_openapi_jsonl(source, cache)
    return cache


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Resolver API", "version": "1.0.0"},
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
                    "properties": {
                        "status": {"$ref": "#/components/schemas/UserStatus"}
                    },
                },
                "UserStatus": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "x-codegen": {"resource": "users"},
                },
            }
        },
        "x-codegen": {"resources": {"users": {"name": "users"}}},
    }
