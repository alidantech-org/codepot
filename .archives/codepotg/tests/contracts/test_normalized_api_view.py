from __future__ import annotations

from contracts.normalized import DiagnosticCategory, ResolutionState
from contracts.normalized_api import NormalizedApiView
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_normalized_api_view_preserves_schema_values_refs_and_composition() -> None:
    graph = InferenceEngine().infer(_document())

    contract = build_api_contract(graph)
    normalized = contract.meta["normalized"]

    assert isinstance(normalized, NormalizedApiView)
    assert contract.meta["loss_count"] == 0
    assert normalized.loss_count == 0
    assert normalized.schemas.count == len(contract.schemas.all)
    assert normalized.operations.count == len(contract.operations)
    assert normalized.resources.count == len(contract.resources)

    user = normalized.schemas.by_id["User"]
    assert user.source.raw["type"] == "object"
    assert user.source.extensions["x-project"]["owner"] == "identity"
    assert user.types == ("object",)
    assert user.constraints.default.is_set
    assert user.constraints.default.is_null
    assert user.constraints.const.value == {"kind": "user"}
    assert user.constraints.examples.value == ({"id": "one"},)
    assert user.constraints.min_properties.value == 1
    assert user.constraints.max_properties.value == 10
    assert user.dependent_required["status"] == ("statusReason",)
    assert user.pattern_properties["^x-"] .inline["type"] == "string"

    status_field = user.fields.by_id["status"]
    assert status_field.schema_use.ref is not None
    assert status_field.schema_use.ref.ref == "#/components/schemas/UserStatus"
    assert status_field.schema_use.ref.state == ResolutionState.RESOLVED
    assert status_field.schema_use.is_resolved
    assert status_field.source.raw["description"] == "Current status"

    list_schema = normalized.schemas.by_id["UserList"]
    assert list_schema.items.ref is not None
    assert list_schema.items.ref.ref == "#/components/schemas/User"
    assert list_schema.constraints.min_items.value == 1
    assert list_schema.constraints.unique_items.value is True

    result = normalized.schemas.by_id["UserResult"]
    assert [composition.kind for composition in result.compositions] == ["oneOf"]
    assert tuple(reference.ref for reference in result.compositions[0].refs) == (
        "#/components/schemas/User",
        "#/components/schemas/Error",
    )

    assert normalized.schemas.group("models")
    assert normalized.schemas.group("enums")
    assert normalized.resources.by_id["users"].operations.count == 1
    assert normalized.resources.by_id["users"].schemas.count >= 2


def test_normalized_api_view_preserves_unknown_and_unresolved_values() -> None:
    document = _document()
    document["components"]["schemas"]["Broken"] = {
        "type": "object",
        "properties": {
            "missing": {"$ref": "#/components/schemas/DoesNotExist"},
        },
        "futureSchemaKeyword": {"enabled": True},
    }

    contract = build_api_contract(InferenceEngine().infer(document))
    normalized: NormalizedApiView = contract.meta["normalized"]
    broken = normalized.schemas.by_id["Broken"]

    assert broken.source.raw["futureSchemaKeyword"]["enabled"] is True
    assert any(
        diagnostic.category == DiagnosticCategory.RAW_ONLY
        and diagnostic.source_path.endswith("futureSchemaKeyword")
        for diagnostic in broken.source.diagnostics
    )
    missing = broken.fields.by_id["missing"].schema_use.ref
    assert missing is not None
    assert missing.state == ResolutionState.MISSING
    assert not missing.is_resolved
    assert missing.ref == "#/components/schemas/DoesNotExist"
    assert missing.diagnostics[0].category == DiagnosticCategory.UNRESOLVED
    assert normalized.unresolved_count >= 1
    assert normalized.loss_count == 0


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "info": {"title": "Normalized API", "version": "1.0.0"},
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
                                    "schema": {"$ref": "#/components/schemas/UserList"}
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "UserStatus": {
                    "type": "string",
                    "enum": ["active", "inactive"],
                    "x-codegen": {"kind": "enum", "resource": "users"},
                },
                "User": {
                    "type": "object",
                    "default": None,
                    "const": {"kind": "user"},
                    "examples": [{"id": "one"}],
                    "minProperties": 1,
                    "maxProperties": 10,
                    "dependentRequired": {"status": ["statusReason"]},
                    "patternProperties": {"^x-": {"type": "string"}},
                    "properties": {
                        "id": {"type": "string"},
                        "status": {
                            "$ref": "#/components/schemas/UserStatus",
                            "description": "Current status",
                        },
                        "statusReason": {"type": ["string", "null"]},
                    },
                    "x-project": {"owner": "identity"},
                    "x-codegen": {"kind": "model", "resource": "users"},
                },
                "UserList": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/User"},
                    "minItems": 1,
                    "uniqueItems": True,
                    "x-codegen": {"kind": "dto", "resource": "users"},
                },
                "Error": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
                "UserResult": {
                    "oneOf": [
                        {"$ref": "#/components/schemas/User"},
                        {"$ref": "#/components/schemas/Error"},
                    ],
                    "x-codegen": {"kind": "dto", "resource": "users"},
                },
            }
        },
        "x-codegen": {
            "resources": {
                "users": {
                    "name": "users",
                    "route": "/users",
                    "info": {"explain": "User operations"},
                }
            }
        },
    }
