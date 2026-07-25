from __future__ import annotations

import json
from pathlib import Path

from inference.engine import InferenceEngine
from openapi.jsonl import build_selected_openapi_document, compile_openapi_jsonl


def test_selected_operation_loads_parent_path_and_reachable_schema_only(
    tmp_path: Path,
) -> None:
    source = tmp_path / "openapi.json"
    source.write_text(json.dumps(_document()), encoding="utf-8")
    cache = tmp_path / "cache"
    compile_openapi_jsonl(source, cache)

    result = build_selected_openapi_document(cache, {"operations"})

    assert result.selections == ("operations",)
    assert result.document["openapi"] == "3.1.0"
    assert result.document["info"]["title"] == "Selected API"
    assert result.document["x-project"] == {"owner": "codepotg"}
    assert set(result.document["paths"]) == {"/users"}
    assert result.document["paths"]["/users"]["x-codegen"]["resource"]["name"] == (
        "users"
    )
    assert result.document["paths"]["/users"]["get"]["operationId"] == "listUsers"
    assert set(result.document["components"]["schemas"]) == {"User"}
    assert "Unused" not in result.document["components"]["schemas"]
    assert result.records_loaded == 2
    assert result.dependency_records_loaded == 1
    assert result.unresolved_refs == ()

    graph = InferenceEngine().infer(result.document)
    assert {operation.operation_id for operation in graph.operations} == {"listUsers"}
    assert {schema.name for schema in graph.schemas} == {"User"}
    assert {resource.name for resource in graph.resources} == {"users"}


def test_selected_enum_does_not_load_unrelated_paths_or_models(tmp_path: Path) -> None:
    source = tmp_path / "openapi.json"
    source.write_text(json.dumps(_document()), encoding="utf-8")
    cache = tmp_path / "cache"
    compile_openapi_jsonl(source, cache)

    result = build_selected_openapi_document(cache, {"enums"})

    assert result.document["paths"] == {}
    assert set(result.document["components"]["schemas"]) == {"UserStatus"}
    assert result.document["components"]["schemas"]["UserStatus"]["enum"] == [
        "active",
        "disabled",
    ]
    assert result.records_loaded == 1
    assert result.dependency_records_loaded == 0


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Selected API", "version": "1.0.0"},
        "servers": [{"url": "https://example.test"}],
        "x-project": {"owner": "codepotg"},
        "paths": {
            "/users": {
                "x-codegen": {"resource": {"name": "users", "path": ["platform"]}},
                "get": {
                    "operationId": "listUsers",
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
                },
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "x-codegen": {"kind": "model", "resource": "users"},
                    "properties": {"id": {"type": "string"}},
                },
                "UserStatus": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "x-codegen": {"kind": "enum", "resource": "users"},
                },
                "Unused": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                },
            }
        },
    }
