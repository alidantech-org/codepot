from __future__ import annotations

import json
from pathlib import Path

import pytest

from openapi.loader import load_openapi_document


@pytest.mark.parametrize("openapi_version", ["3.0.3", "3.1.0"])
def test_codepotx_style_openapi_documents_are_loadable(
    tmp_path: Path,
    openapi_version: str,
) -> None:
    document_path = tmp_path / "openapi.json"
    payload = {
        "openapi": openapi_version,
        "info": {
            "title": "CodepotX compatibility fixture",
            "version": "1.0.0",
        },
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {
                        "200": {
                            "description": "Users",
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
                    "x-codegen": {
                        "kind": "query",
                        "info": {"summary": "List users"},
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                    },
                    "x-codegen": {
                        "kind": "model",
                        "entity": {"name": "User"},
                    },
                }
            }
        },
        "x-codegen": {
            "frontends": [
                {
                    "name": "admin",
                    "screens": [],
                    "components": [],
                }
            ]
        },
    }
    document_path.write_text(json.dumps(payload), encoding="utf-8")

    document = load_openapi_document(document_path)

    assert document.openapi_version == openapi_version
    assert document.title == "CodepotX compatibility fixture"
    assert "User" in document.schemas
    assert document.raw["x-codegen"] == payload["x-codegen"]
    assert document.paths["/users"]["get"]["x-codegen"]["kind"] == "query"
