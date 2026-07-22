"""Tests for compiler-resolved operation UI metadata."""

from __future__ import annotations

from pathlib import Path

from src.inference.operations.engine import infer_operations
from src.openapi.document import OpenApiDocument


def test_infer_operation_ui_metadata_reflects_compiler_resolved_ui() -> None:
    document = OpenApiDocument(
        path=Path("openapi.json"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "UI API", "version": "v1"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "x-codegen": {
                            "ui": {
                                "enabled": True,
                                "role": "list",
                                "inferred": True,
                                "inferenceSource": "compiler",
                                "inferenceReason": "GET collection route",
                            }
                        },
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        },
    )

    operation = infer_operations(document)[0]

    assert operation.ui == {
        "enabled": True,
        "role": "list",
        "inferred": True,
        "inferenceSource": "compiler",
        "inferenceReason": "GET collection route",
    }


def test_infer_operation_ui_metadata_defaults_to_disabled() -> None:
    document = OpenApiDocument(
        path=Path("openapi.json"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "UI API", "version": "v1"},
            "paths": {
                "/auth/login": {
                    "post": {
                        "operationId": "login",
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        },
    )

    operation = infer_operations(document)[0]

    assert operation.ui == {
        "enabled": False,
        "role": None,
        "inferred": False,
        "inferenceSource": None,
        "inferenceReason": None,
    }
