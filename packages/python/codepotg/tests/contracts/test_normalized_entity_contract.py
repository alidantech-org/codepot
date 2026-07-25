from __future__ import annotations

from contracts.normalized import DiagnosticCategory, ResolutionState
from contracts.normalized_entity_contract import NormalizedEntityContract
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_entity_inheritance_visibility_queries_relations_and_rules_are_normalized() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    entities: NormalizedEntityContract = contract.meta["normalized_entities"]

    timestamped = entities.base_entities.by_id["Timestamped"]
    assert timestamped.is_base
    assert timestamped.is_abstract
    assert timestamped.declared_fields.by_id["createdAt"].readonly.value is True

    user = entities.entities.by_id["UserEntity"]
    assert user.resource is not None and user.resource.is_resolved
    assert user.schema.ref is not None and user.schema.ref.is_resolved
    assert user.store == "users"
    assert user.visibility == ("backend", "storage", "api")
    assert user.extends[0].state == ResolutionState.RESOLVED
    assert [item.id for item in user.inherited_fields.all] == [
        "createdAt",
        "updatedAt",
        "tenantId",
    ]
    assert [item.id for item in user.effective_fields.all] == [
        "createdAt",
        "updatedAt",
        "tenantId",
        "name",
        "status",
    ]

    tenant = user.effective_fields.by_id["tenantId"]
    assert tenant.overrides == "tenantId"
    assert tenant.override_origin == "Timestamped"
    assert tenant.editable.value is True
    assert tenant.query.operators == ("exact", "sortable", "tenant_scope")
    assert tenant.query.unknown_operators == ("tenant_scope",)
    assert tenant.query.diagnostics[0].category == DiagnosticCategory.UNSUPPORTED

    assert user.backend_fields.by_id["internalNote"].is_backend_only
    assert "internalNote" not in user.public_fields.by_id
    assert "internalNote" in user.storage_fields.by_id
    assert "name" in user.editable_fields.by_id
    assert "createdAt" in user.readonly_fields.by_id
    assert "tenantId" in user.queryable_fields.by_id

    relation = user.relations.by_id["roles"]
    assert relation.cardinality == "many_to_many"
    assert relation.target is not None and relation.target.is_resolved
    assert relation.local_fields == ("tenantId", "userId")
    assert relation.foreign_fields == ("tenantId", "roleId")
    assert relation.on_delete == "cascade"
    assert relation.on_update == "restrict"
    assert relation.nullable.value is False
    assert relation.owning.value is True
    assert relation.inverse == "users"
    assert relation.is_to_many
    assert not relation.is_to_one

    unique = user.constraints.by_id["user_email"]
    assert unique.kind == "unique"
    assert unique.fields == ("tenantId", "email")
    assert unique.unique.value is True

    rule = user.constraints.by_id["active_name"].rule
    assert rule is not None and rule.is_when
    assert rule.condition is not None and rule.condition.is_equal
    assert rule.then is not None and rule.then.is_not_null
    assert rule.otherwise is not None
    assert rule.otherwise.op == "custom_rule"
    assert rule.otherwise.diagnostics[0].category == DiagnosticCategory.UNSUPPORTED
    assert rule.otherwise.raw_arguments["severity"] == "warning"

    assert entities.unresolved_count == 0
    assert entities.cycle_count == 0
    assert contract.meta["loss_count"] == 0


def test_entity_cycles_and_missing_targets_are_preserved() -> None:
    document = _document()
    document["x-codegen"]["entities"]["First"] = {
        "extends": ["Second"],
        "relations": [
            {
                "name": "missing",
                "targetEntity": "MissingEntity",
                "cardinality": "many_to_one",
            }
        ],
    }
    document["x-codegen"]["entities"]["Second"] = {"extends": ["First"]}

    contract = build_api_contract(InferenceEngine().infer(document))
    entities: NormalizedEntityContract = contract.meta["normalized_entities"]

    first = entities.entities.by_id["First"]
    assert first.extends[0].is_resolved
    assert first.relations.by_id["missing"].target is not None
    assert first.relations.by_id["missing"].target.state == ResolutionState.MISSING
    assert entities.unresolved_count >= 1
    assert entities.cycle_count >= 1
    assert any(
        diagnostic.category == DiagnosticCategory.CYCLE
        for diagnostic in entities.diagnostics
    )


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Entity API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "OK"}},
                    "x-codegen": {"resource": {"name": "users"}},
                }
            }
        },
        "components": {
            "schemas": {
                "UserModel": {
                    "type": "object",
                    "x-codegen": {"kind": "model", "resource": "users"},
                }
            }
        },
        "x-codegen": {
            "resources": {"users": {"name": "users", "route": "/users"}},
            "baseEntities": {
                "Timestamped": {
                    "abstract": True,
                    "visibility": ["backend", "storage"],
                    "fields": {
                        "createdAt": {
                            "type": "datetime",
                            "readonly": True,
                            "generated": True,
                        },
                        "updatedAt": {
                            "type": "datetime",
                            "readonly": True,
                            "managed": True,
                        },
                        "tenantId": {
                            "type": "string",
                            "readonly": True,
                            "query": {"exact": True},
                        },
                    },
                }
            },
            "entities": {
                "RoleEntity": {
                    "resource": "users",
                    "store": "roles",
                    "fields": {"roleId": {"type": "string"}},
                },
                "UserEntity": {
                    "resource": "users",
                    "schema": "#/components/schemas/UserModel",
                    "store": "users",
                    "kind": "aggregate",
                    "visibility": ["backend", "storage", "api"],
                    "extends": ["Timestamped"],
                    "fields": {
                        "tenantId": {
                            "type": "string",
                            "editable": True,
                            "query": {
                                "exact": True,
                                "sortable": True,
                                "operators": ["tenant_scope"],
                            },
                        },
                        "name": {"type": "string", "editable": True},
                        "status": {
                            "type": "string",
                            "selectable": True,
                            "query": {"oneOf": True},
                        },
                    },
                    "backendFields": {
                        "internalNote": {
                            "type": "string",
                            "readonly": True,
                        }
                    },
                    "relations": {
                        "roles": {
                            "cardinality": "many_to_many",
                            "targetEntity": "RoleEntity",
                            "localFields": ["tenantId", "userId"],
                            "foreignFields": ["tenantId", "roleId"],
                            "onDelete": "cascade",
                            "onUpdate": "restrict",
                            "nullable": False,
                            "owning": True,
                            "inverse": "users",
                        }
                    },
                    "unique": {
                        "user_email": {"fields": ["tenantId", "email"]}
                    },
                    "constraints": {
                        "active_name": {
                            "kind": "rule",
                            "rule": {
                                "op": "when",
                                "condition": {
                                    "op": "eq",
                                    "field": "status",
                                    "value": "active",
                                },
                                "then": {"op": "not_null", "field": "name"},
                                "otherwise": {
                                    "op": "custom_rule",
                                    "field": "status",
                                    "severity": "warning",
                                },
                            },
                        }
                    },
                },
            },
        },
    }
