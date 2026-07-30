from __future__ import annotations

import json
from pathlib import Path

from openapi.jsonl import JsonlIndexStore, compile_openapi_jsonl


def test_semantic_codegen_mentions_are_indexed_without_normalization(tmp_path: Path) -> None:
    source = tmp_path / "openapi.json"
    source.write_text(json.dumps(_document()), encoding="utf-8")
    cache = tmp_path / "cache"

    result = compile_openapi_jsonl(source, cache)
    store = JsonlIndexStore(cache)

    assert _items(store, "access", "users.read") >= {
        "operation:get:/users",
        "access:users.read",
    }
    assert _items(store, "permission", "users:read") == {"access:users.read"}
    assert _items(store, "entity", "UserEntity") >= {
        "entity:UserEntity",
        "entity:UserRoleEntity",
    }
    assert _items(store, "relation", "roles") == {"entity:UserEntity"}
    assert _items(store, "frontend", "admin") >= {
        "frontend:admin",
        "operation:get:/users",
    }
    assert _items(store, "screen", "users-list") == {"frontend:admin"}
    assert _items(store, "template", "users/list.tsx.j2") == {"frontend:admin"}
    assert _items(store, "import", "@app/users") == {"frontend:admin"}
    assert _items(store, "generated_file", "src/users/list.tsx") == {
        "frontend:admin"
    }

    assert result.mentions_written > 0


def _items(store: JsonlIndexStore, index: str, value: str) -> set[str]:
    return {
        str(fact["item"])
        for fact in store.find_mentions(index, value)
        if isinstance(fact.get("item"), str)
    }


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Semantic Index API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "x-codegen": {
                        "resource": {"name": "users"},
                        "access": {"policy": "users.read"},
                        "frontend": "admin",
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
        "components": {"schemas": {"User": {"type": "object"}}},
        "x-codegen": {
            "resources": {"users": {"name": "users"}},
            "access": {
                "users.read": {
                    "name": "users.read",
                    "permissions": ["users:read"],
                }
            },
            "entities": {
                "UserEntity": {
                    "name": "UserEntity",
                    "resource": "users",
                    "relations": [
                        {"name": "roles", "targetEntity": "UserRoleEntity"}
                    ],
                },
                "UserRoleEntity": {
                    "name": "UserRoleEntity",
                    "resource": "users",
                    "entity": "UserEntity",
                },
            },
            "frontends": {
                "admin": {
                    "name": "admin",
                    "screens": [{"name": "users-list"}],
                    "template": "users/list.tsx.j2",
                    "imports": ["@app/users"],
                    "output": "src/users/list.tsx",
                }
            },
        },
    }
