from __future__ import annotations

from contracts.normalized import DiagnosticCategory, ResolutionState
from contracts.normalized_schema_contract import (
    NormalizedSchemaContract,
    SchemaBoundaryKind,
)
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_complete_json_schema_keywords_are_typed_and_preserved() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    schemas: NormalizedSchemaContract = contract.meta["normalized_schemas"]
    value = schemas.by_id["Complete"]

    assert schemas.count == 2
    assert schemas.dialect.value == "https://json-schema.org/draft/2020-12/schema"
    assert value.title.value == "Complete value"
    assert value.summary.value == "All schema facts"
    assert value.description.value == "Complete schema description"
    assert value.types == ("object", "null")
    assert value.format.value == "custom"
    assert value.nullable.value is True
    assert value.default.is_set and value.default.is_null
    assert value.const.value == {"kind": "complete"}
    assert value.example.value == {"kind": "complete"}
    assert value.examples.value == ({"kind": "complete"},)
    assert value.enum.value == ("one", "two")
    assert value.required == ("address",)

    assert value.minimum.value == 0
    assert value.maximum.value == 100
    assert value.exclusive_minimum.value == -1
    assert value.exclusive_maximum.value == 101
    assert value.multiple_of.value == 5
    assert value.min_length.value == 1
    assert value.max_length.value == 64
    assert value.pattern.value == "^[a-z]+$"
    assert value.content_encoding.value == "base64"
    assert value.content_media_type.value == "application/json"
    assert value.content_schema.ref is not None
    assert value.content_schema.ref.state == ResolutionState.RESOLVED

    assert value.items.ref is not None
    assert value.prefix_items[0].inline["type"] == "string"
    assert value.contains.ref is not None
    assert value.min_contains.value == 1
    assert value.max_contains.value == 2
    assert value.min_items.value == 1
    assert value.max_items.value == 10
    assert value.unique_items.value is True
    assert value.unevaluated_items.kind == SchemaBoundaryKind.FORBIDDEN

    assert value.properties["address"].ref is not None
    assert value.additional_properties.kind == SchemaBoundaryKind.SCHEMA
    assert value.additional_properties.schema.ref is not None
    assert value.pattern_properties["^x-"].inline["type"] == "string"
    assert value.property_names.inline["pattern"] == "^[a-z]"
    assert value.min_properties.value == 1
    assert value.max_properties.value == 12
    assert value.dependent_required["address"] == ("kind",)
    assert value.dependent_schemas["kind"].inline["required"] == ("address",)
    assert value.unevaluated_properties.kind == SchemaBoundaryKind.SCHEMA

    assert value.all_of[0].ref is not None
    assert value.any_of[0].inline["type"] == "string"
    assert value.one_of[0].ref is not None
    assert value.not_schema.inline["required"] == ("forbidden",)
    assert value.if_schema.inline["properties"]["kind"]["const"] == "complete"
    assert value.then_schema.inline["required"] == ("address",)
    assert value.else_schema.inline["required"] == ("fallback",)
    assert value.defs["Local"].inline["type"] == "integer"

    assert value.discriminator["propertyName"] == "kind"
    assert value.read_only.value is False
    assert value.write_only.value is True
    assert value.deprecated.value is False
    assert value.external_docs["url"] == "https://example.com/schema"
    assert value.schema_id.value == "https://example.com/complete"
    assert value.anchor.value == "complete"
    assert value.dynamic_anchor.value == "node"
    assert value.dynamic_ref.value == "#node"
    assert value.dialect.value == "https://json-schema.org/draft/2020-12/schema"
    assert value.source.raw["x-project"]["owner"] == "contracts"
    assert value.diagnostics == ()
    assert schemas.loss_count == 0
    assert schemas.unresolved_count == 0


def test_malformed_schema_boundary_is_preserved_and_diagnosed() -> None:
    document = _document()
    document["components"]["schemas"]["Complete"]["additionalProperties"] = "invalid"

    contract = build_api_contract(InferenceEngine().infer(document))
    schemas: NormalizedSchemaContract = contract.meta["normalized_schemas"]
    boundary = schemas.by_id["Complete"].additional_properties

    assert boundary.kind == SchemaBoundaryKind.MALFORMED
    assert boundary.value.value == "invalid"
    assert boundary.diagnostics[0].category == DiagnosticCategory.MALFORMED
    assert contract.meta["loss_count"] == 0


def _document() -> dict[str, object]:
    schema_ref = {"$ref": "#/components/schemas/Address"}
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "info": {"title": "Schema API", "version": "1.0.0"},
        "paths": {},
        "components": {
            "schemas": {
                "Address": {
                    "type": "object",
                    "properties": {"line": {"type": "string"}},
                },
                "Complete": {
                    "$id": "https://example.com/complete",
                    "$anchor": "complete",
                    "$dynamicAnchor": "node",
                    "$dynamicRef": "#node",
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$defs": {"Local": {"type": "integer"}},
                    "title": "Complete value",
                    "summary": "All schema facts",
                    "description": "Complete schema description",
                    "type": ["object", "null"],
                    "format": "custom",
                    "nullable": True,
                    "default": None,
                    "const": {"kind": "complete"},
                    "example": {"kind": "complete"},
                    "examples": [{"kind": "complete"}],
                    "enum": ["one", "two"],
                    "minimum": 0,
                    "maximum": 100,
                    "exclusiveMinimum": -1,
                    "exclusiveMaximum": 101,
                    "multipleOf": 5,
                    "minLength": 1,
                    "maxLength": 64,
                    "pattern": "^[a-z]+$",
                    "contentEncoding": "base64",
                    "contentMediaType": "application/json",
                    "contentSchema": schema_ref,
                    "items": schema_ref,
                    "prefixItems": [{"type": "string"}, schema_ref],
                    "contains": schema_ref,
                    "minContains": 1,
                    "maxContains": 2,
                    "minItems": 1,
                    "maxItems": 10,
                    "uniqueItems": True,
                    "unevaluatedItems": False,
                    "properties": {"address": schema_ref},
                    "required": ["address"],
                    "additionalProperties": schema_ref,
                    "patternProperties": {"^x-": {"type": "string"}},
                    "propertyNames": {"pattern": "^[a-z]"},
                    "minProperties": 1,
                    "maxProperties": 12,
                    "dependentRequired": {"address": ["kind"]},
                    "dependentSchemas": {"kind": {"required": ["address"]}},
                    "unevaluatedProperties": {"type": "boolean"},
                    "allOf": [schema_ref],
                    "anyOf": [{"type": "string"}],
                    "oneOf": [schema_ref, {"type": "null"}],
                    "not": {"required": ["forbidden"]},
                    "if": {"properties": {"kind": {"const": "complete"}}},
                    "then": {"required": ["address"]},
                    "else": {"required": ["fallback"]},
                    "discriminator": {"propertyName": "kind"},
                    "readOnly": False,
                    "writeOnly": True,
                    "deprecated": False,
                    "externalDocs": {"url": "https://example.com/schema"},
                    "x-project": {"owner": "contracts"},
                },
            }
        },
    }
