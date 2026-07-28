from __future__ import annotations

from contracts.normalized import ResolutionState
from contracts.normalized_domains import NormalizedDomainView
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_http_security_access_entities_and_frontends_are_normalized() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    domains: NormalizedDomainView = contract.meta["normalized_domains"]

    assert domains.servers.count == 1
    server = domains.servers.all[0]
    assert server.url == "https://{region}.example.com"
    assert server.variables.by_id["region"].default.value == "us"

    bearer = domains.security_schemes.by_id["bearerAuth"]
    assert bearer.type == "http"
    assert bearer.scheme == "bearer"
    assert bearer.bearer_format == "JWT"
    assert domains.root_security[0].uses[0].scheme.is_resolved
    assert domains.root_security[0].uses[0].scheme.target is bearer

    path = domains.paths.by_id["/users/{id}"]
    assert path.summary == "User path"
    assert path.parameters.count == 1
    operation = domains.operations.by_id["getUser"]
    assert operation.path == "/users/{id}"
    assert operation.method == "get"
    assert operation.security_is_override
    assert operation.security == ()
    assert operation.declared_parameters.count == 2
    assert operation.effective_parameters.count == 2
    assert operation.effective_parameters.get("id") is not None
    assert operation.effective_parameters.get("expand") is not None
    assert operation.request_body is not None
    assert operation.request_body.required.value is False
    body_media = operation.request_body.content.by_id["application/json"]
    assert body_media.schema_use.ref is not None
    assert body_media.schema_use.ref.state == ResolutionState.RESOLVED
    assert body_media.schema_use.ref.name == "UserFilter"
    assert operation.responses.by_id["200"].is_success
    assert operation.responses.by_id["404"].is_error
    assert operation.primary_response is operation.responses.by_id["200"]
    assert operation.callbacks["onUpdate"]

    policy = domains.access.by_id["users.read"]
    assert policy.public.value is False
    assert policy.authenticated.value is True
    assert policy.roles == ("admin", "support")
    assert policy.permissions == ("users:read",)

    base = domains.base_entities.by_id["Timestamped"]
    assert base.abstract.value is True
    user = domains.entities.by_id["UserEntity"]
    assert user.schema_use.ref is not None
    assert user.schema_use.ref.state == ResolutionState.RESOLVED
    assert user.table == "users"
    assert user.extends[0].is_resolved
    assert user.extends[0].name == "Timestamped"
    assert user.declared_fields.by_id["email"].unique.value is True
    assert user.declared_fields.by_id["email"].query_operators == (
        "exact",
        "contains",
    )
    backend = user.backend_fields.by_id["internalNote"]
    assert backend.backend_only.value is True
    relation = user.relations.by_id["company"]
    assert relation.target.is_resolved
    assert relation.target.name == "CompanyEntity"
    assert relation.local_fields == ("companyId",)
    assert relation.foreign_fields == ("id",)
    assert relation.is_to_one
    assert user.constraints.by_id["email-present"].kind == "rule"

    frontend = domains.frontends.by_id["admin"]
    assert frontend.route_prefix == "/admin"
    component = frontend.components.by_id["user-card"]
    assert component.props.ref is not None
    assert component.props.ref.state == ResolutionState.RESOLVED
    assert component.uses[0].operation is not None
    assert component.uses[0].operation.is_resolved
    screen = frontend.screens.by_id["user-detail"]
    assert screen.route == "/users/{id}"
    assert screen.full_route == "/admin/users/{id}"
    assert screen.params.ref is not None
    assert screen.params.ref.is_resolved
    assert screen.components == ("user-card",)

    assert domains.unresolved_count == 0
    assert contract.meta["unresolved_count"] == 0


def test_unresolved_domain_references_are_preserved_and_reported() -> None:
    document = _document()
    document["x-codegen"]["entities"]["BrokenEntity"] = {
        "extends": ["MissingBase"],
        "relations": [
            {
                "name": "missing",
                "cardinality": "many_to_one",
                "targetEntity": "MissingEntity",
            }
        ],
    }
    document["x-codegen"]["frontends"]["broken"] = {
        "components": {
            "broken": {
                "uses": [
                    {
                        "alias": "missing",
                        "operation": "missingOperation",
                    }
                ]
            }
        }
    }

    contract = build_api_contract(InferenceEngine().infer(document))
    domains: NormalizedDomainView = contract.meta["normalized_domains"]
    broken = domains.entities.by_id["BrokenEntity"]

    assert broken.extends[0].state == ResolutionState.EXTERNAL
    assert broken.relations.by_id["missing"].target.state == ResolutionState.EXTERNAL
    use = domains.frontends.by_id["broken"].components.by_id["broken"].uses[0]
    assert use.operation is not None
    assert use.operation.state == ResolutionState.EXTERNAL
    assert use.operation.ref == "missingOperation"


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Domain API", "version": "1.0.0"},
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
        "security": [{"bearerAuth": []}],
        "paths": {
            "/users/{id}": {
                "summary": "User path",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {
                    "operationId": "getUser",
                    "summary": "Get user",
                    "security": [],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "description": "Operation override",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "expand",
                            "in": "query",
                            "style": "form",
                            "explode": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserFilter"
                                },
                                "example": {"includeInactive": False},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                    "callbacks": {
                        "onUpdate": {"{$request.body#/url}": {}}
                    },
                    "x-codegen": {"resource": {"name": "users"}},
                },
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "x-codegen": {"kind": "model", "resource": "users"},
                },
                "UserFilter": {"type": "object"},
                "UserPath": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                },
            },
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
        },
        "x-codegen": {
            "resources": {"users": {"name": "users"}},
            "access": {
                "users.read": {
                    "public": False,
                    "authenticated": True,
                    "roles": ["admin", "support"],
                    "permissions": ["users:read"],
                }
            },
            "baseEntities": {
                "Timestamped": {
                    "abstract": True,
                    "fields": {
                        "createdAt": {"type": "string", "readonly": True}
                    },
                }
            },
            "entities": {
                "CompanyEntity": {
                    "schema": "#/components/schemas/User",
                    "table": "companies",
                },
                "UserEntity": {
                    "resource": "users",
                    "schema": "#/components/schemas/User",
                    "table": "users",
                    "extends": ["Timestamped"],
                    "fields": {
                        "email": {
                            "type": "string",
                            "unique": True,
                            "query": ["exact", "contains"],
                        },
                        "companyId": {"type": "string"},
                    },
                    "backendFields": {
                        "internalNote": {"type": "string"}
                    },
                    "relations": [
                        {
                            "name": "company",
                            "cardinality": "many_to_one",
                            "targetEntity": "CompanyEntity",
                            "localFields": ["companyId"],
                            "foreignFields": ["id"],
                            "onDelete": "restrict",
                        }
                    ],
                    "constraints": {
                        "email-present": {
                            "kind": "rule",
                            "fields": ["email"],
                            "expression": {"op": "notNull", "field": "email"},
                        }
                    },
                },
            },
            "frontends": {
                "admin": {
                    "title": "Admin",
                    "routePrefix": "/admin",
                    "components": {
                        "user-card": {
                            "props": {"$ref": "#/components/schemas/User"},
                            "uses": [
                                {
                                    "alias": "loadUser",
                                    "operation": "getUser",
                                    "purpose": "load",
                                }
                            ],
                        }
                    },
                    "screens": {
                        "user-detail": {
                            "route": "/users/{id}",
                            "params": {
                                "$ref": "#/components/schemas/UserPath"
                            },
                            "components": ["user-card"],
                            "uses": [
                                {
                                    "alias": "loadUser",
                                    "operation": "getUser",
                                }
                            ],
                        }
                    },
                }
            },
        },
    }
