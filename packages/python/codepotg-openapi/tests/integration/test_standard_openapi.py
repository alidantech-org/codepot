from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest
from codepotg_openapi import OpenApiSourceAdapter


def _document(*, title: str = "Orders API", with_codegen: bool = False) -> str:
    value: dict[str, object] = {
        "openapi": "3.0.3",
        "info": {"title": title, "version": "2026.1"},
        "paths": {
            "/orders/{id}": {
                "get": {
                    "operationId": "getOrder",
                    "tags": ["orders"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Order"}
                                }
                            },
                        },
                        "404": {"description": "missing"},
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "Order": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {"type": "string", "readOnly": True},
                        "total": {"type": "number", "minimum": 0},
                    },
                }
            }
        },
    }
    if with_codegen:
        value["x-codegen"] = {"version": "2", "groups": {"orders": {}}}
    return json.dumps(value)


def _semantic_signature(contract) -> tuple[object, ...]:
    return (
        contract.id,
        contract.name,
        contract.version,
        tuple(
            (
                group.id,
                group.name,
                group.path,
                tuple((schema.id, schema.name, schema.kind) for schema in group.schemas),
                tuple(
                    (
                        operation.id,
                        operation.name,
                        operation.inputs,
                        operation.outputs,
                        operation.failures,
                        operation.effects,
                        operation.facets,
                    )
                    for operation in group.operations
                ),
            )
            for group in contract.groups
        ),
    )


def test_public_facade_returns_core_valid_immutable_contract() -> None:
    result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="orders", content=_document()),
        CancellationToken(),
    )
    assert result.contract is not None
    assert result.digest is not None and len(result.digest) == 64
    assert not result.diagnostics.has_errors
    contract = result.contract
    assert contract.name.value == "Orders API"
    group = next(item for item in contract.groups if item.name.value == "orders")
    assert {item.name.value for item in group.operations} == {"getOrder"}
    all_schemas = tuple(schema for owner in contract.groups for schema in owner.schemas)
    assert any(item.name.value == "Order" for item in all_schemas)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        contract.version = "changed"  # type: ignore[misc]


def test_semantic_content_changes_digest_with_same_source_id() -> None:
    adapter = OpenApiSourceAdapter()
    first = adapter.normalize(
        SourceAdapterRequest(source_id="same", content=_document(title="First")),
        CancellationToken(),
    )
    second = adapter.normalize(
        SourceAdapterRequest(source_id="same", content=_document(title="Second")),
        CancellationToken(),
    )
    assert first.contract is not None and second.contract is not None
    assert first.contract.name != second.contract.name
    assert first.digest != second.digest


def test_equivalent_json_and_yaml_have_same_semantic_digest() -> None:
    adapter = OpenApiSourceAdapter()
    json_result = adapter.normalize(
        SourceAdapterRequest(source_id="same", content=_document()),
        CancellationToken(),
    )
    yaml_result = adapter.normalize(
        SourceAdapterRequest(
            source_id="same",
            content="""openapi: 3.0.3
info: {title: Orders API, version: '2026.1'}
paths:
  /orders/{id}:
    get:
      operationId: getOrder
      tags: [orders]
      parameters:
        - {name: id, in: path, required: true, schema: {type: string}}
      responses:
        '200':
          description: found
          content:
            application/json:
              schema: {$ref: '#/components/schemas/Order'}
        '404': {description: missing}
components:
  schemas:
    Order:
      type: object
      required: [id]
      properties:
        id: {type: string, readOnly: true}
        total: {type: number, minimum: 0}
""",
        ),
        CancellationToken(),
    )
    assert json_result.contract is not None and yaml_result.contract is not None
    assert _semantic_signature(json_result.contract) == _semantic_signature(yaml_result.contract)
    assert json_result.digest == yaml_result.digest


def test_unimplemented_codegen_is_truthful_and_policy_controlled() -> None:
    adapter = OpenApiSourceAdapter()
    tolerant = adapter.normalize(
        SourceAdapterRequest(source_id="codegen", content=_document(with_codegen=True)),
        CancellationToken(),
    )
    assert tolerant.contract is not None
    assert "OA_XCODEGEN_NOT_IMPLEMENTED" in {item.code for item in tolerant.diagnostics}
    strict = adapter.normalize(
        SourceAdapterRequest(
            source_id="codegen",
            content=_document(with_codegen=True),
            options=(("xCodegenPolicy", "strict"),),
        ),
        CancellationToken(),
    )
    assert strict.contract is None
    assert {item.code for item in strict.diagnostics} == {"OA_XCODEGEN_NOT_IMPLEMENTED"}
