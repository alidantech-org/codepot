from __future__ import annotations

from contracts.normalized import ResolutionState
from contracts.normalized_frontend_contract import NormalizedFrontendContract
from inference.engine import InferenceEngine
from inference.lossless_contract import build_api_contract


def test_frontend_folders_components_screens_and_uses_are_normalized() -> None:
    contract = build_api_contract(InferenceEngine().infer(_document()))
    frontends: NormalizedFrontendContract = contract.meta["normalized_frontends"]

    assert frontends.count == 1
    admin = frontends.by_id["admin"]
    assert admin.title == "Admin Console"
    assert admin.route_prefix == "/admin"
    assert admin.folders["components"] == "src/components"
    assert admin.folders["screens"] == "src/screens"

    table = admin.components.by_id["user-table"]
    assert table.folder == "components"
    assert table.props.ref is not None and table.props.ref.is_resolved
    assert table.schemas[0].ref is not None and table.schemas[0].ref.is_resolved
    assert table.tags == ("users", "table")
    assert table.notes.explain == ("Render user rows",)
    assert table.uses[0].alias == "loadUsers"
    assert table.uses[0].operation is not None
    assert table.uses[0].operation.state == ResolutionState.RESOLVED
    assert table.uses[0].schema.ref is not None
    assert table.uses[0].schema.ref.state == ResolutionState.RESOLVED
    assert table.uses[0].purpose == "list"

    screen = admin.screens.by_id["users"]
    assert screen.route == "/users"
    assert screen.full_route == "/admin/users"
    assert screen.folder == "screens"
    assert screen.params.ref is not None and screen.params.ref.is_resolved
    assert screen.query.ref is not None and screen.query.ref.is_resolved
    assert screen.body.ref is not None and screen.body.ref.is_resolved
    assert screen.response.ref is not None and screen.response.ref.is_resolved
    assert screen.components == ("user-table", "user-filter")
    assert screen.placement["user-table"]["area"] == "main"
    assert screen.placement["user-filter"]["area"] == "sidebar"
    assert screen.uses[0].operation is not None
    assert screen.uses[0].operation.is_resolved
    assert screen.tags == ("users", "list")
    assert screen.notes.ux == ("Keep filters visible",)

    assert admin.operations.count == 1
    assert admin.operations.by_id["listUsers"].id == "listUsers"
    assert set(admin.schemas.by_id) == {
        "UserFilter",
        "UserList",
        "UserModel",
    }
    assert admin.source.raw["futureFrontendFlag"] is True
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
