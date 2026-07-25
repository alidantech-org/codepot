from __future__ import annotations

from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_flat_entities_become_stable_compatibility_items() -> None:
    contract = build_api_contract(InferenceEngine().infer(_flat_document()))

    assert [entity.name.raw.o for entity in contract.entities] == ["UserEntity"]
    entity = contract.entities[0]
    assert entity.id == "UserEntity"
    assert entity.store == "users"
    assert [field.id for field in entity.fields] == ["id", "name"]
    assert [field.id for field in entity.backend_fields] == ["internalNote"]


def test_nested_resource_entity_shape_remains_compatible() -> None:
    document = _base_document()
    document["x-codegen"] = {
        "entities": {
            "users": {
                "UserEntity": {
                    "store": "users",
                }
            }
        }
    }

    contract = build_api_contract(InferenceEngine().infer(document))

    assert [entity.name.raw.o for entity in contract.entities] == ["UserEntity"]
    assert contract.entities[0].id == "users.UserEntity"
    assert contract.entities[0].resource == "users"


def _flat_document() -> dict[str, object]:
    document = _base_document()
    document["x-codegen"] = {
        "entities": {
            "UserEntity": {
                "store": "users",
                "fields": {
                    "id": {"type": "string", "readonly": True},
                    "name": {"type": "string", "editable": True},
                },
                "backendFields": {
                    "internalNote": {"type": "string"},
                },
            }
        }
    }
    return document


def _base_document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Entity API", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}},
    }
