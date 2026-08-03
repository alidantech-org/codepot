from __future__ import annotations

from contracts.normalized_api import NormalizedApiView
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_normalized_source_registry_preserves_openapi_and_codegen_objects() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    normalized: NormalizedApiView = contract.meta["normalized"]
    objects = normalized.raw_objects

    assert objects["info"].raw["contact"]["name"] == "API Team"
    assert objects["server:0"].raw["url"] == "https://{region}.example.com"
    assert objects["server:0:variable:region"].raw["default"] == "us"
    assert objects["path:/users"].raw["summary"] == "Users path"
    assert objects["path:/users:parameter:0"].raw["name"] == "tenantId"
    assert objects["operation:listUsers"].raw["operationId"] == "listUsers"
    assert objects["operation:listUsers:parameter:0"].raw["name"] == "limit"
    assert objects["operation:listUsers:requestBody"].raw["required"] is False
    assert (
        objects[
            "operation:listUsers:requestBody:media:application/json"
        ].raw["schema"]["$ref"]
        == "#/components/schemas/UserFilter"
    )
    assert objects["operation:listUsers:response:200"].raw["description"] == "OK"
    assert (
        objects[
            "operation:listUsers:response:200:media:application/json"
        ].raw["schema"]["type"]
        == "array"
    )
    assert objects["operation:listUsers:response:200:header:X-Total"].raw[
        "description"
    ] == "Total rows"
    assert objects["operation:listUsers:response:200:link:next"].raw[
        "operationId"
    ] == "listUsers"
    assert "operation:listUsers:callback:onChange" in objects

    assert objects["component:parameters:TraceId"].raw["name"] == "traceId"
    assert objects["component:requestBodies:UserFilterBody"].raw["required"] is True
    assert objects["component:responses:Unauthorized"].raw["description"] == "Unauthorized"
    assert objects["component:securitySchemes:bearerAuth"].raw["scheme"] == "bearer"

    assert objects["x-codegen:access:users.read"].raw["permissions"] == (
        "users:read",
    )
    assert objects["x-codegen:entities:UserEntity"].raw["table"] == "users"
    assert objects[
        "x-codegen:entities:UserEntity:relations:0"
    ].raw["targetEntity"] == "RoleEntity"
    assert objects[
        "x-codegen:entities:UserEntity:backendFields:internalNote"
    ].raw["backendOnly"] is True
    assert objects["x-codegen:frontends:admin"].raw["routePrefix"] == "/admin"
    assert objects["x-codegen:frontends:admin:screens:0"].raw["route"] == "/users"
    assert objects[
        "x-codegen:frontends:admin:components:user-table"
    ].raw["purpose"] == "list"
    assert objects["x-codegen:resources:users:hook:audit"].raw["handler"] == "auditUsers"

    assert normalized.loss_count == 0
    assert normalized.raw_only_count >= 1


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Source Registry API",
            "version": "1.0.0",
            "contact": {"name": "API Team"},
        },
        "servers": [
            {
                "url": "https://{region}.example.com",
                "variables": {
                    "region": {
                        "default": "us",
                        "enum": ["us", "eu"],
                    }
                },
            }
        ],
        "paths": {
            "/users": {
                "summary": "Users path",
                "parameters": [
                    {
                        "name": "tenantId",
                        "in": "header",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {
                    "operationId": "listUsers",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserFilter"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "X-Total": {"description": "Total rows"}
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/User"
                                        },
                                    }
                                }
                            },
                            "links": {
                                "next": {"operationId": "listUsers"}
                            },
                        }
                    },
                    "callbacks": {
                        "onChange": {
                            "{$request.body#/callbackUrl}": {
                                "post": {
                                    "responses": {
                                        "200": {"description": "Callback accepted"}
                                    }
                                }
                            }
                        }
                    },
                    "x-codegen": {"resource": {"name": "users"}},
                },
            }
        },
        "components": {
            "schemas": {
                "User": {"type": "object"},
                "UserFilter": {"type": "object"},
            },
            "parameters": {
                "TraceId": {
                    "name": "traceId",
                    "in": "header",
                    "schema": {"type": "string"},
                }
            },
            "requestBodies": {
                "UserFilterBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserFilter"
                            }
                        }
                    },
                }
            },
            "responses": {
                "Unauthorized": {"description": "Unauthorized"}
            },
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                }
            },
        },
        "x-codegen": {
            "resources": {
                "users": {
                    "name": "users",
                    "hooks": {
                        "audit": {"handler": "auditUsers"}
                    },
                }
            },
            "access": {
                "users.read": {
                    "permissions": ["users:read"]
                }
            },
            "entities": {
                "UserEntity": {
                    "resource": "users",
                    "table": "users",
                    "backendFields": {
                        "internalNote": {"backendOnly": True}
                    },
                    "relations": [
                        {
                            "name": "roles",
                            "targetEntity": "RoleEntity",
                        }
                    ],
                },
                "RoleEntity": {"resource": "users"},
            },
            "frontends": {
                "admin": {
                    "routePrefix": "/admin",
                    "components": {
                        "user-table": {"purpose": "list"}
                    },
                    "screens": [
                        {"name": "users", "route": "/users"}
                    ],
                    "futureFrontendFlag": True,
                }
            },
        },
    }
