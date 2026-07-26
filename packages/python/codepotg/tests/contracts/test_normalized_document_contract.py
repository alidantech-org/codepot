"""Tests for the typed lossless OpenAPI document contract."""

from __future__ import annotations

from emission.contexts.bounded import bounded_graph_context
from inference.lossless_contract import build_api_contract
from inference.models import InferenceGraph
from languages.debug.adapter import DebugLanguageAdapter
from src.contracts.normalized_document_contract import (
    build_normalized_document_contract,
)


def _complete_document() -> dict:
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "info": {
            "title": "Complete API",
            "summary": "Summary",
            "description": "Description",
            "termsOfService": "https://example.test/terms",
            "contact": {
                "name": "API Team",
                "url": "https://example.test/contact",
                "email": "api@example.test",
            },
            "license": {
                "name": "Apache-2.0",
                "identifier": "Apache-2.0",
                "url": "https://example.test/license",
            },
            "version": "v1",
        },
        "servers": [
            {
                "url": "https://{region}.example.test",
                "description": "Regional server",
                "variables": {
                    "region": {
                        "default": "eu",
                        "description": "Region",
                        "enum": ["eu", "us"],
                    }
                },
            }
        ],
        "paths": {
            "/widgets": {
                "summary": "Widgets",
                "description": "Widget operations",
                "parameters": [{"name": "tenant", "in": "header"}],
                "get": {
                    "operationId": "listWidgets",
                    "responses": {"200": {"description": "OK"}},
                    "x-operation-extra": True,
                },
            }
        },
        "webhooks": {
            "widgetChanged": {
                "post": {
                    "operationId": "widgetChanged",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
        "components": {
            "schemas": {"Widget": {"type": "object"}},
            "responses": {"Ok": {"description": "OK"}},
            "parameters": {"Limit": {"name": "limit", "in": "query"}},
            "examples": {"Widget": {"value": {"id": "1"}}},
            "requestBodies": {"Widget": {"content": {}}},
            "headers": {"Trace": {"schema": {"type": "string"}}},
            "securitySchemes": {"Bearer": {"type": "http", "scheme": "bearer"}},
            "links": {"Next": {"operationId": "listWidgets"}},
            "callbacks": {"Changed": {"{$request.body#/url}": {}}},
            "pathItems": {"Widgets": {"get": {"responses": {}}}},
        },
        "security": [{"Bearer": []}],
        "tags": [
            {
                "name": "widgets",
                "description": "Widget tag",
                "externalDocs": {
                    "description": "Tag docs",
                    "url": "https://example.test/tags/widgets",
                },
            }
        ],
        "externalDocs": {
            "description": "API docs",
            "url": "https://example.test/docs",
        },
        "x-project-extra": {"enabled": True},
        "futureStandardField": {"preserved": True},
    }


def test_document_contract_exposes_all_top_level_openapi_families() -> None:
    document = build_normalized_document_contract(_complete_document())

    assert document.openapi.value == "3.1.0"
    assert document.json_schema_dialect.is_authored
    assert document.info.title.value == "Complete API"
    assert document.info.contact.email.value == "api@example.test"
    assert document.info.license.identifier.value == "Apache-2.0"
    assert document.servers[0].variables["region"].enum == ("eu", "us")

    path = document.paths["/widgets"]
    assert path.summary.value == "Widgets"
    assert len(path.parameters) == 1
    assert path.operations["get"].extensions["x-operation-extra"] is True
    assert "widgetChanged" in document.webhooks

    components = document.components
    assert set(components.schemas) == {"Widget"}
    assert set(components.responses) == {"Ok"}
    assert set(components.parameters) == {"Limit"}
    assert set(components.examples) == {"Widget"}
    assert set(components.request_bodies) == {"Widget"}
    assert set(components.headers) == {"Trace"}
    assert set(components.security_schemes) == {"Bearer"}
    assert set(components.links) == {"Next"}
    assert set(components.callbacks) == {"Changed"}
    assert set(components.path_items) == {"Widgets"}

    assert document.security[0]["Bearer"] == ()
    assert document.tags[0].name.value == "widgets"
    assert document.tags[0].external_docs.url.value.endswith("/tags/widgets")
    assert document.external_docs.url.value == "https://example.test/docs"
    assert document.extensions["x-project-extra"]["enabled"] is True
    assert document.raw["futureStandardField"]["preserved"] is True
    assert document.loss_count == 0
    assert any(
        diagnostic.source_path == "$.futureStandardField"
        for diagnostic in document.diagnostics
    )


def test_document_contract_uses_safe_missing_values() -> None:
    document = build_normalized_document_contract({})

    assert document.openapi.is_set is False
    assert document.info.title.is_set is False
    assert document.servers == ()
    assert dict(document.paths) == {}
    assert dict(document.webhooks) == {}
    assert document.security == ()
    assert document.tags == ()
    assert document.external_docs.url.is_set is False
    assert document.loss_count == 0


def test_lossless_inference_attaches_and_bounded_context_reuses_document_contract(
    tmp_path,
) -> None:
    raw = _complete_document()
    graph = InferenceGraph(
        title="Complete API",
        openapi_version="3.1.0",
        api_version="v1",
        description="Description",
        servers=(),
        resources=(),
        schemas=(),
        operations=(),
        dependencies=(),
        raw=raw,
    )

    api = build_api_contract(graph)
    document = api.meta["normalized_document"]
    contract = DebugLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path / "out",
        dry_run=True,
    )
    context = bounded_graph_context(contract)

    assert context["document_contract"] is document
    assert context["document_contract"].raw["openapi"] == "3.1.0"
    assert "api" not in context.public_keys
    assert "api" in context.selection_keys
