from __future__ import annotations

import json
from pathlib import Path

import pytest

from emission.planning import (
    JsonlSelectionPlanner,
    OutputRegistryLimits,
    OutputStatus,
    SelectionEmission,
    VirtualOutputConflictError,
    VirtualOutputRegistry,
)
from openapi.jsonl import JsonlSelectionStore, SelectionGroup, SelectionRecord, SelectionScope
from openapi.jsonl.compiler import compile_openapi_jsonl


def test_one_source_record_is_loaded_once_for_multiple_emissions(tmp_path: Path) -> None:
    cache = _compile_fixture(tmp_path)
    store = JsonlSelectionStore(cache)
    registry = VirtualOutputRegistry()
    planner = JsonlSelectionPlanner(store, registry=registry)

    emissions = (
        SelectionEmission(
            id="dto-type",
            template_path="templates/dto.type.ts.j2",
            output_path=lambda context: f"types/{_name(context)}.ts",
            symbols=lambda context: (_name(context),),
        ),
        SelectionEmission(
            id="dto-zod",
            template_path="templates/dto.zod.ts.j2",
            output_path=lambda context: f"schemas/{_name(context)}.schema.ts",
            symbols=lambda context: (f"{_name(context)}Schema",),
        ),
    )

    plan = planner.plan("dtos", emissions)

    assert plan.selection == "schemas.emit_dtos"
    assert plan.records_loaded == 1
    assert store.load_count == 1
    assert [item.output_path.as_posix() for item in plan.outputs] == [
        "types/CreateUserDto.ts",
        "schemas/CreateUserDto.schema.ts",
    ]
    assert len(registry.find_ref("#/components/schemas/CreateUserDto")) == 2

    handle = next(store.iter_handles("dtos"))
    assert store.load(handle).key == "schema:CreateUserDto"
    assert store.load_count == 1

    written = registry.mark_written(
        selection="schemas.emit_dtos",
        emission="dto-type",
        source_key="schema:CreateUserDto",
    )
    assert written.status == OutputStatus.WRITTEN
    assert registry.find_ref(
        "#/components/schemas/CreateUserDto",
        written_only=True,
    ) == (written,)


def test_aggregate_and_resource_plans_do_not_load_raw_records(tmp_path: Path) -> None:
    cache = _compile_fixture(tmp_path)
    store = JsonlSelectionStore(cache)

    all_planner = JsonlSelectionPlanner(store)
    all_plan = all_planner.plan(
        "schemas.all",
        (
            SelectionEmission(
                id="all-schemas",
                template_path="templates/all.ts.j2",
                output_path=lambda context: "types/index.ts",
            ),
        ),
        scope=SelectionScope.ALL,
    )
    assert all_plan.records_loaded == 0
    assert all_plan.groups[0].count == 2
    assert all_plan.outputs[0].source_key == "selection:schemas.all:all"

    resource_planner = JsonlSelectionPlanner(store)
    resource_plan = resource_planner.plan(
        "operations",
        (
            SelectionEmission(
                id="resource-operations",
                template_path="templates/resource.operations.ts.j2",
                output_path=lambda context: f"resources/{_resource(context)}/operations.ts",
            ),
        ),
        scope=SelectionScope.RESOURCE,
    )
    assert resource_plan.records_loaded == 0
    assert [(group.resource, group.count) for group in resource_plan.groups] == [
        ("users", 1)
    ]
    assert resource_plan.outputs[0].output_path.as_posix() == (
        "resources/users/operations.ts"
    )
    assert store.load_count == 0


def test_virtual_registry_normalizes_paths_and_rejects_ambiguity() -> None:
    registry = VirtualOutputRegistry(OutputRegistryLimits(max_entries=2))
    first = registry.register(
        selection="schemas.emit_dtos",
        emission="dto-type",
        source_key="schema:CreateUserDto",
        source_ref="#/components/schemas/CreateUserDto",
        template_path=r"templates\dto.ts.j2",
        output_path=r"types\create-user.dto.ts",
    )

    assert first.template_path.as_posix() == "templates/dto.ts.j2"
    assert first.output_path.as_posix() == "types/create-user.dto.ts"

    with pytest.raises(VirtualOutputConflictError, match="planned more than once"):
        registry.register(
            selection="schemas.emit_dtos",
            emission="dto-type",
            source_key="schema:CreateUserDto",
            source_ref="#/components/schemas/CreateUserDto",
            template_path="templates/dto.ts.j2",
            output_path="types/create-user.dto.ts",
        )

    with pytest.raises(VirtualOutputConflictError, match="Output path collision"):
        registry.register(
            selection="schemas.emit_enums",
            emission="enum-type",
            source_key="schema:UserStatus",
            source_ref="#/components/schemas/UserStatus",
            template_path="templates/enum.ts.j2",
            output_path="types/create-user.dto.ts",
        )

    registry.register(
        selection="schemas.emit_enums",
        emission="enum-type",
        source_key="schema:UserStatus",
        source_ref="#/components/schemas/UserStatus",
        template_path="templates/enum.ts.j2",
        output_path="types/user-status.ts",
    )
    with pytest.raises(VirtualOutputConflictError, match="exceeded 2 entries"):
        registry.register(
            selection="schemas.emit_models",
            emission="model-type",
            source_key="schema:User",
            source_ref="#/components/schemas/User",
            template_path="templates/model.ts.j2",
            output_path="types/user.ts",
        )


def _name(context: SelectionRecord | SelectionGroup) -> str:
    return context.key.split(":")[-1]


def _resource(context: SelectionRecord | SelectionGroup) -> str:
    if isinstance(context, SelectionGroup) and context.resource:
        return context.resource
    raise AssertionError("Expected a resource selection group")


def _compile_fixture(tmp_path: Path) -> Path:
    source = tmp_path / "openapi.json"
    source.write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "info": {"title": "Planner API", "version": "1.0.0"},
                "paths": {
                    "/users": {
                        "post": {
                            "operationId": "createUser",
                            "x-codegen": {"resource": {"name": "users"}},
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/CreateUserDto"
                                        }
                                    }
                                }
                            },
                            "responses": {"201": {"description": "Created"}},
                        }
                    }
                },
                "components": {
                    "schemas": {
                        "CreateUserDto": {
                            "type": "object",
                            "x-codegen": {"kind": "dto", "resource": "users"},
                            "properties": {"name": {"type": "string"}},
                        },
                        "UserStatus": {
                            "type": "string",
                            "enum": ["active", "inactive"],
                            "x-codegen": {"resource": "users"},
                        },
                    }
                },
                "x-codegen": {"resources": {"users": {"name": "users"}}},
            }
        ),
        encoding="utf-8",
    )
    cache = tmp_path / "cache"
    compile_openapi_jsonl(source, cache)
    return cache
