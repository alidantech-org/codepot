from __future__ import annotations

from contracts.normalized import ResolutionState, ValueOrigin
from contracts.normalized_codegen_contract import NormalizedCodegenContract
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract
from tests.fixtures.openapi import load_real_contract


def test_real_resource_operation_cache_access_and_sources_are_normalized(
    real_openapi_path,
) -> None:
    contract = load_real_contract(real_openapi_path)
    codegen: NormalizedCodegenContract = contract.meta["normalized_codegen"]

    resource = codegen.resources.by_id["apps"]
    assert resource.route == "/platform/apps"
    assert resource.tags == ("platform", "apps")
    assert resource.ui.enabled.value is True
    assert resource.ui.effective_enabled.value is True
    assert resource.operations.by_id["findApps"].id == "findApps"
    assert resource.schemas.by_id["AppListQuery"].id == "AppListQuery"
    assert resource.entities.by_id["App"].id == "App"

    auth = codegen.resources.by_id["auth"]
    assert "setSessionCookies" in auth.hooks.by_id
    assert auth.hooks.by_id["setSessionCookies"].source.raw["phase"] == (
        "afterSuccess"
    )

    operation = codegen.operations.by_id["findApps"]
    assert operation.name_value.value == "findApps"
    assert operation.name_value.origin == ValueOrigin.AUTHORED
    assert operation.role.value == "list"
    assert operation.role.origin == ValueOrigin.AUTHORED
    assert operation.tags == ("platform", "apps", "list")
    assert operation.ui.enabled.value is True
    assert operation.ui.effective_enabled.value is True
    assert operation.parameter_target.ref is not None
    assert operation.parameter_target.ref.state == ResolutionState.RESOLVED
    assert operation.parameter_target.ref.name == "AppListQuery"

    assert operation.sources.count == 1
    assert operation.primary_source is operation.sources.by_id["apps"]
    assert operation.primary_source.response_field == "apps"
    assert operation.primary_source.item.ref is not None
    assert operation.primary_source.item.ref.state == ResolutionState.RESOLVED
    assert operation.primary_source.item.ref.name == "AppPartial"
    assert operation.primary_source.key_field == "id"
    assert operation.primary_source.label_field == "name"
    assert operation.primary_source.value_field is None

    assert operation.access.ref == (
        "#/x-codegen/access/global/authenticated"
    )
    assert operation.access.is_resolved
    assert operation.access.policy is not None
    assert operation.access.policy.target is not None
    assert operation.access.policy.target.id == "global.authenticated"

    create = codegen.operations.by_id["createApp"]
    assert create.role.value == "create"
    assert create.cache.invalidate.operation_names == ("findApps",)
    assert create.cache.invalidate.operations[0].state == ResolutionState.RESOLVED

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
