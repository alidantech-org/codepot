"""Tests for operation target inference."""

from __future__ import annotations

from pathlib import Path

from src.inference.operations.engine import infer_operations
from src.openapi.document import OpenApiDocument


def test_infer_operation_target_from_parameter_target_metadata() -> None:
    document = OpenApiDocument(
        path=Path("openapi.json"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Query API", "version": "v1"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "parameters": [
                            {
                                "name": "page",
                                "in": "query",
                                "schema": {"$ref": "#/components/schemas/SharedPage"},
                            }
                        ],
                        "x-codegen": {
                            "parameters": {
                                "target": {"$ref": "#/components/schemas/UserListQuery"},
                            }
                        },
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        },
    )

    operation = infer_operations(document)[0]

    assert operation.target is not None
    assert operation.target.ref == "#/components/schemas/UserListQuery"
    assert operation.target.source == "x-codegen.parameters.target"
    assert operation.target.inferred_roles == ("query",)
    assert operation.target.locations == ("query",)


def test_infer_parameter_target_keeps_query_role_with_path_and_referenced_query() -> None:
    document = OpenApiDocument(
        path=Path("openapi.json"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Query API", "version": "v1"},
            "paths": {
                "/companies/{companyId}/availability": {
                    "get": {
                        "operationId": "getCompanyAvailability",
                        "parameters": [
                            {
                                "name": "companyId",
                                "in": "path",
                                "required": True,
                                "schema": {"$ref": "#/components/schemas/SharedMongoId"},
                            },
                            {
                                "$ref": "#/components/parameters/AvailabilityFieldsQueryParam",
                            },
                        ],
                        "x-codegen": {
                            "parameters": {
                                "target": {
                                    "$ref": "#/components/schemas/CompanyAvailabilityDetailQuery",
                                },
                            }
                        },
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
            "components": {
                "parameters": {
                    "AvailabilityFieldsQueryParam": {
                        "name": "fields",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/CompanyAvailabilitySelect",
                            },
                        },
                    }
                }
            },
        },
    )

    operation = infer_operations(document)[0]

    assert operation.target is not None
    assert operation.target.ref == "#/components/schemas/CompanyAvailabilityDetailQuery"
    assert operation.target.source == "x-codegen.parameters.target"
    assert operation.target.inferred_roles == ("params", "query")
    assert operation.target.locations == ("path", "query")


def test_infer_operation_resource_from_path_level_codegen_ref() -> None:
    document = OpenApiDocument(
        path=Path("openapi.yaml"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "x-codegen": {
                "resources": {
                    "apps": {
                        "name": "apps",
                        "path": ["platform"],
                    }
                }
            },
            "paths": {
                "/platform/apps": {
                    "x-codegen": {
                        "resource": {"$ref": "#/x-codegen/resources/apps"},
                    },
                    "get": {
                        "operationId": "findApps",
                        "x-codegen": {
                            "parameters": {
                                "target": {"$ref": "#/components/schemas/AppListQuery"},
                            },
                            "operation": {
                                "name": "findApps",
                                "role": "list",
                            },
                            "ui": {
                                "enabled": True,
                                "role": "list",
                                "inferred": False,
                            },
                            "sources": {
                                "apps": {
                                    "responseField": "apps",
                                    "item": {"$ref": "#/components/schemas/AppPartial"},
                                    "key": "id",
                                    "label": "name",
                                }
                            },
                        },
                        "responses": {"200": {"description": "OK"}},
                    },
                }
            },
        },
    )

    operation = infer_operations(document)[0]

    assert operation.resource is not None
    assert operation.resource.name == "apps"
    assert operation.resource.path == ("platform",)
    assert operation.target is not None
    assert operation.target.ref == "#/components/schemas/AppListQuery"
    assert operation.ui["enabled"] is True
    assert operation.ui["role"] == "list"
