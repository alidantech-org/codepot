from __future__ import annotations

from contracts.normalized import ResolutionState
from contracts.normalized_frontend_contract import NormalizedFrontendContract
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract
from tests.fixtures.openapi import load_real_contract


def test_real_frontend_components_screens_and_uses_are_normalized(
    real_openapi_path,
) -> None:
    contract = load_real_contract(real_openapi_path)
    frontends: NormalizedFrontendContract = contract.meta["normalized_frontends"]

    assert frontends.count == 1
    admin = frontends.by_id["admin"]
    assert admin.title == "Admin"
    assert admin.route_prefix == "/admin"
    assert admin.source.raw["folders"] == ("admin",)

    table = admin.components.by_id["AppsTable"]
    assert table.props.ref is not None and table.props.ref.is_resolved
    assert table.props.ref.name == "AdminAppsTableProps"
    assert table.schemas[0].ref is not None
    assert table.schemas[0].ref.is_resolved
    assert table.schemas[0].ref.name == "AppPartial"
    assert table.notes.explain == (
        "Displays apps returned by the list operation.",
    )
    assert table.notes.ux == (
        "Support loading, empty, and pagination states.",
    )
    assert table.uses[0].alias == "findApps"
    assert table.uses[0].operation is not None
    assert table.uses[0].operation.state == ResolutionState.RESOLVED
    assert table.uses[0].operation.name == "findApps"

    screen = admin.screens.by_id["AppsListScreen"]
    assert screen.route == "/apps"
    assert screen.full_route == "/admin/apps"
    assert screen.components == ("table", "filters")
    assert screen.placement["table"]["$ref"] == (
        "#/x-codegen/frontends/admin/components/AppsTable"
    )
    assert screen.placement["filters"]["$ref"] == (
        "#/x-codegen/frontends/admin/components/AppsFilters"
    )
    assert screen.uses[0].operation is not None
    assert screen.uses[0].operation.is_resolved
    assert screen.uses[0].operation.name == "findApps"
    assert screen.notes.implement == (
        "Render filters above the table and keep pagination in URL state.",
    )

    detail = admin.screens.by_id["AppDetailScreen"]
    assert detail.route == "/apps/:id"
    assert detail.full_route == "/admin/apps/:id"
    assert detail.params.ref is not None and detail.params.ref.is_resolved
    assert detail.params.ref.name == "AppRouteParams"

    assert "findApps" in admin.operations.by_id
    assert "getAppById" in admin.operations.by_id
    assert "updateApp" in admin.operations.by_id
    assert "AdminAppsTableProps" in admin.schemas.by_id
    assert "AppListQuery" in admin.schemas.by_id
    assert "AppPublic" in admin.schemas.by_id
    assert frontends.unresolved_count == 0
    assert contract.meta["loss_count"] == 0


def test_missing_frontend_uses_remain_inspectable() -> None:
    document = _document()
    document["x-codegen"]["frontends"]["admin"]["components"]["broken"] = {
        "props": "#/components/schemas/MissingProps",
        "uses": [
            {
                "alias": "missing",
                "operation": "missingOperation",
                "schema": "#/components/schemas/MissingSchema",
            }
        ],
    }

    contract = build_api_contract(InferenceEngine().infer(document))
    frontends: NormalizedFrontendContract = contract.meta["normalized_frontends"]
    broken = frontends.by_id["admin"].components.by_id["broken"]

    assert broken.props.ref is not None
    assert broken.props.ref.state == ResolutionState.MISSING
    assert broken.uses[0].operation is not None
    assert broken.uses[0].operation.state == ResolutionState.MISSING
    assert broken.uses[0].schema.ref is not None
    assert broken.uses[0].schema.ref.state == ResolutionState.MISSING
    assert frontends.unresolved_count >= 3


def _document() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Frontend API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
        "components": {
            "schemas": {
                "UserModel": {"type": "object"},
                "UserFilter": {"type": "object"},
                "UserList": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/UserModel"},
                },
            }
        },
        "x-codegen": {
            "frontends": {
                "admin": {
                    "title": "Admin Console",
                    "routePrefix": "/admin",
                    "folders": {
                        "components": "src/components",
                        "screens": "src/screens",
                    },
                    "components": {
                        "user-table": {
                            "folder": "components",
                            "props": "#/components/schemas/UserList",
                            "schemas": ["#/components/schemas/UserModel"],
                            "uses": [
                                {
                                    "alias": "loadUsers",
                                    "operation": "listUsers",
                                    "schema": "#/components/schemas/UserList",
                                    "purpose": "list",
                                    "tags": ["users"],
                                }
                            ],
                            "tags": ["users", "table"],
                            "info": {"explain": "Render user rows"},
                        },
                        "user-filter": {
                            "folder": "components",
                            "props": "#/components/schemas/UserFilter",
                        },
                    },
                    "screens": {
                        "users": {
                            "route": "/users",
                            "folder": "screens",
                            "params": "#/components/schemas/UserFilter",
                            "query": "#/components/schemas/UserFilter",
                            "body": "#/components/schemas/UserModel",
                            "response": "#/components/schemas/UserList",
                            "components": {
                                "user-table": {"area": "main"},
                                "user-filter": {"area": "sidebar"},
                            },
                            "uses": [
                                {
                                    "alias": "loadUsers",
                                    "operation": "listUsers",
                                    "schema": "#/components/schemas/UserList",
                                }
                            ],
                            "tags": ["users", "list"],
                            "info": {"ux": "Keep filters visible"},
                        }
                    },
                    "futureFrontendFlag": True,
                }
            }
        },
    }
