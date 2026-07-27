from __future__ import annotations

import json

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapter, SourceAdapterRequest
from codepotg.testing import assert_source_adapter_conformance

from codepotg_openapi import OpenApiSourceAdapter


def _document(title: str = "Pets API") -> str:
    return json.dumps(
        {
            "openapi": "3.1.0",
            "info": {"title": title, "version": "1.0.0"},
            "paths": {
                "/pets": {
                    "get": {
                        "operationId": "listPets",
                        "tags": ["pets"],
                        "responses": {
                            "200": {
                                "description": "ok",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Pet"},
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
                    "Pet": {
                        "type": "object",
                        "required": ["id"],
                        "properties": {"id": {"type": "string"}},
                    }
                }
            },
        }
    )


def test_adapter_satisfies_public_protocol_and_conformance() -> None:
    adapter = OpenApiSourceAdapter()
    assert isinstance(adapter, SourceAdapter)
    assert_source_adapter_conformance(
        adapter,
        SourceAdapterRequest(source_id="pets", content=_document()),
    )


def test_invalid_source_returns_diagnostics_not_internal_exception() -> None:
    result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="invalid", content="openapi: ["),
        CancellationToken(),
    )
    assert result.contract is None
    assert result.digest is None
    assert result.diagnostics.has_errors
    assert all(item.code != "OA_INTERNAL_NORMALIZATION" for item in result.diagnostics)


def test_composed_cancellation_returns_stable_diagnostic() -> None:
    cancellation = CancellationToken()
    cancellation.cancel("test cancellation")
    result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="cancelled", content=_document()),
        cancellation,
    )
    assert result.contract is None
    assert {item.code for item in result.diagnostics} == {"OA_CANCELLED"}
