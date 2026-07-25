from __future__ import annotations

from contracts.normalized import ResolutionState, ValueOrigin
from contracts.normalized_codegen_contract import NormalizedCodegenContract
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_resource_operation_cache_access_runtime_and_sources_are_normalized() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    codegen: NormalizedCodegenContract = contract.meta["normalized_codegen"]

    resource = codegen.resources.by_id["users"]
    assert resource.route == "/users"
    assert resource.tags == ("users", "identity")
    assert resource.ui.enabled.value is True
    assert resource.ui.effective_enabled.value is True
    assert resource.operations.by_id["listUsers"].id == "listUsers"
    assert resource.schemas.by_id["UserList"].id == "UserList"
    assert resource.entities.by_id["UserEntity"].id == "UserEntity"
    assert resource.access_policies[0].is_resolved
    assert resource.hooks.by_id["audit"].handler == "auditUsers"

    operation = codegen.operations.by_id["listUsers"]
    assert operation.name_value.value == "List users"
    assert operation.role.value == "list"
    assert operation.role.origin == ValueOrigin.AUTHORED
    assert operation.tags == ("users",)
    assert operation.ui.enabled.value is False
    assert operation.ui.effective_enabled.value is False
    assert operation.parameter_target.ref is not None
    assert operation.parameter_target.ref.state == ResolutionState.RESOLVED
    assert operation.query_schema.ref is not None
    assert operation.response_schema.ref is not None

    assert operation.sources.count == 1
    assert operation.primary_source is operation.sources.by_id["users"]
    assert operation.primary_source.response_field == "items"
    assert operation.primary_source.item.ref is not None
    assert operation.primary_source.item.ref.state == ResolutionState.RESOLVED
    assert operation.primary_source.key_field == "id"
    assert operation.primary_source.label_field == "name"
    assert operation.primary_source.value_field == "id"

    assert operation.cache.enabled.value is True
    assert operation.cache.read.enabled.value is True
    assert operation.cache.read.ttl_seconds.value == 60
    assert operation.cache.read.stale_seconds.value == 10
    assert operation.cache.read.scope.value == "user"
    assert operation.cache.read.key_fields == ("tenantId",)
    assert operation.cache.read.tags == ("users",)
    assert operation.cache.invalidate.operation_names == (
        "listUsers",
        "missingOperation",
    )
    assert operation.cache.invalidate.operations[0].state == ResolutionState.RESOLVED
    assert operation.cache.invalidate.operations[1].state == ResolutionState.MISSING
    assert operation.cache.invalidate.resources[0].state == ResolutionState.RESOLVED
    assert operation.cache.invalidate.resources[1].state == ResolutionState.MISSING
    assert operation.cache.invalidate.tags == ("users",)
    assert operation.cache.invalidate.all.value is False

    assert operation.access.ref == "users.read"
    assert operation.access.is_resolved
    assert operation.transport.inbound.ip.value is True
    assert operation.transport.inbound.user_agent.value is True
    assert operation.transport.inbound.headers["x-tenant-id"]["required"] is True
    assert operation.transport.inbound.cookies["session"]["required"] is True
    assert operation.transport.outbound.headers["x-total"]["source"] == "response"
    assert operation.transport.outbound.cookies["refresh"]["httpOnly"] is True

    assert [item.phase for item in operation.hooks.all] == [
        "before_handler",
        "after_success",
    ]
    assert all(item.is_resolved for item in operation.hooks.all)
    assert operation.hooks.before_handler[0].hook.target.handler == "auditUsers"
    assert codegen.unresolved_count == 2
    assert contract.meta["loss_count"] == 0


def test_unknown_policy_and_hook_uses_remain_inspectable() -> None:
    document = _document()
    operation = document["paths"]["/users"]["get"]["x-codegen"]
    operation["access"] = "missing.policy"
    operation["runtime"]["hooks"]["afterError"] = ["missingHook"]

    contract = build_api_contract(InferenceEngine().infer(document))
    codegen: NormalizedCodegenContract = contract.meta["normalized_codegen"]
    value = codegen.operations.by_id["listUsers"]

    assert value.access.ref == "missing.policy"
    assert not value.access.is_resolved
    assert value.hooks.after_error[0].ref == "missingHook"
    assert not value.hooks.after_error[0].is_resolved
    assert codegen.unresolved_count >= 4


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Codegen API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "OK"}},
                    "x-codegen": {
                        "resource": {"name": "users"},
                        "name": "List users",
                        "role": "list",
                        "tags": ["users"],
                        "ui": {
                            "enabled": False,
                            "infer": True,
                            "source": "operation",
                            "reason": "Explicitly hidden",
                        },
                        "parameters": {
                            "target": "#/components/schemas/UserFilter"
                        },
                        "query": "#/components/schemas/UserFilter",
                        "response": "#/components/schemas/UserList",
                        "sources": {
                            "users": {
                                "responseField": "items",
                                "item": "#/components/schemas/UserList",
                                "keyField": "id",
                                "labelField": "name",
                                "valueField": "id",
                                "description": "User options",
                                "primary": True,
                            }
                        },
                        "cache": {
                            "enabled": True,
                            "read": {
                                "enabled": True,
                                "ttlSeconds": 60,
                                "staleSeconds": 10,
                                "scope": "user",
                                "keyFields": ["tenantId"],
                                "tags": ["users"],
                            },
                            "invalidate": {
                                "operations": ["listUsers", "missingOperation"],
                                "resources": ["users", "missingResource"],
                                "tags": ["users"],
                                "all": False,
                            },
                        },
                        "access": "users.read",
                        "runtime": {
                            "transport": {
                                "inbound": {
                                    "ip": True,
                                    "userAgent": True,
                                    "headers": {
                                        "x-tenant-id": {"required": True}
                                    },
                                    "cookies": {
                                        "session": {"required": True}
                                    },
                                },
                                "outbound": {
                                    "headers": {
                                        "x-total": {"source": "response"}
                                    },
                                    "cookies": {
                                        "refresh": {"httpOnly": True}
                                    },
                                },
                            },
                            "hooks": {
                                "beforeHandler": ["audit"],
                                "afterSuccess": [{"ref": "audit", "order": 2}],
                            },
                        },
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "UserFilter": {
                    "type": "object",
                    "x-codegen": {"kind": "dto", "resource": "users"},
                },
                "UserList": {
                    "type": "array",
                    "items": {"type": "string"},
                    "x-codegen": {"kind": "dto", "resource": "users"},
                },
            }
        },
        "x-codegen": {
            "resources": {
                "users": {
                    "name": "users",
                    "route": "/users",
                    "tags": ["users", "identity"],
                    "ui": {"enabled": True},
                    "accessPolicies": ["users.read"],
                    "hooks": {
                        "audit": {
                            "handler": "auditUsers",
                            "order": 1,
                            "info": {"explain": "Audit user reads"},
                        }
                    },
                }
            },
            "access": {
                "users.read": {
                    "authenticated": True,
                    "permissions": ["users:read"],
                }
            },
            "entities": {
                "UserEntity": {
                    "resource": "users",
                    "schema": "#/components/schemas/UserList",
                    "table": "users",
                }
            },
        },
    }
