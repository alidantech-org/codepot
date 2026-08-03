from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from contracts.path_yaml import path_config_from_yaml
from emission.paths.graph_planner import PathGraphPlanningError, plan_path_graph


@dataclass(frozen=True)
class FakeDependency:
    ref: str
    is_importable: bool = True


@dataclass(frozen=True)
class FakeEmit:
    key: str
    ref: str | None
    dependencies: tuple[FakeDependency, ...] = ()
    resource_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class FakeLang:
    symbol_name: str


@dataclass(frozen=True)
class FakeItem:
    name: str
    emit: FakeEmit
    lang: FakeLang
    resource: str | None = None
    meta: dict[str, object] = field(default_factory=dict)


def test_graph_plans_multiple_emissions_from_one_selection_and_barrel(
    tmp_path: Path,
) -> None:
    _templates(tmp_path, "dto.ts.j2", "dto.schema.ts.j2", "enum.ts.j2", "index.ts.j2")
    dto = _item("CreateUserDto", "dto:create", "#/components/schemas/CreateUserDto")
    enum = _item("UserStatus", "enum:status", "#/components/schemas/UserStatus")
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "dtos", "as": "dto"},
                "enums": {"select": "enums", "as": "enum"},
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", "[dto.name].ts"],
                    "provides": ["dtos"],
                },
                "dto-zod": {
                    "selection": "dtos",
                    "template": "dto.schema.ts.j2",
                    "output": ["schemas", "[dto.name].schema.ts"],
                    "provides": ["dtos"],
                },
                "enum-types": {
                    "selection": "enums",
                    "template": "enum.ts.j2",
                    "output": ["models", "[enum.name].ts"],
                    "provides": ["enums"],
                },
            },
            "barrels": {
                "models-barrel": {
                    "template": "index.ts.j2",
                    "output": ["models", "index.ts"],
                    "exports": ["dto-types", "enum-types"],
                }
            },
        },
        strict=True,
    )

    plan = plan_path_graph(
        config=config,
        base_context={"dtos": (dto,), "enums": (enum,)},
        template_root=tmp_path,
    )

    assert [file.output_path.as_posix() for file in plan.files] == [
        "models/CreateUserDto.ts",
        "models/UserStatus.ts",
        "models/index.ts",
        "schemas/CreateUserDto.schema.ts",
    ]
    barrel = next(file for file in plan.files if file.node_key == "models-barrel")
    assert barrel.depends_on == (
        "models/CreateUserDto.ts",
        "models/UserStatus.ts",
    )
    assert barrel.provides == ("dtos", "enums")
    assert set(plan.registry.find_ref("#/components/schemas/CreateUserDto"))
    assert len(plan.registry.find_emission("dto-types")) == 1
    assert len(plan.registry.find_emission("dto-zod")) == 1


def test_graph_binds_exact_direct_provider_dependency(tmp_path: Path) -> None:
    _templates(tmp_path, "dto.ts.j2", "operation.ts.j2")
    dto_ref = "#/components/schemas/CreateUserDto"
    dto = _item("CreateUserDto", "dto:create", dto_ref)
    operation = _item(
        "createUser",
        "operation:create",
        "#/paths/~1users/post",
        dependencies=(FakeDependency(dto_ref),),
    )
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "dtos", "as": "dto"},
                "operations": {"select": "operations", "as": "operation"},
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", "[dto.name].ts"],
                    "provides": ["dtos"],
                },
                "operations": {
                    "selection": "operations",
                    "template": "operation.ts.j2",
                    "output": ["operations", "[operation.name].ts"],
                    "imports": {"dtos": "dto-types"},
                },
            },
        },
        strict=True,
    )

    plan = plan_path_graph(
        config=config,
        base_context={"dtos": (dto,), "operations": (operation,)},
        template_root=tmp_path,
    )

    operation_file = next(file for file in plan.files if file.node_key == "operations")
    assert operation_file.depends_on == ("models/CreateUserDto.ts",)
    assert plan.files.index(operation_file) > plan.files.index(
        next(file for file in plan.files if file.node_key == "dto-types")
    )


def test_graph_all_scope_provider_covers_each_selected_ref(tmp_path: Path) -> None:
    _templates(tmp_path, "dtos.ts.j2", "operation.ts.j2")
    first_ref = "#/components/schemas/FirstDto"
    second_ref = "#/components/schemas/SecondDto"
    dtos = (
        _item("FirstDto", "dto:first", first_ref),
        _item("SecondDto", "dto:second", second_ref),
    )
    operation = _item(
        "useSecond",
        "operation:second",
        "#/paths/~1second/post",
        dependencies=(FakeDependency(second_ref),),
    )
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "dtos", "as": "dtos", "scope": "all"},
                "operations": {"select": "operations", "as": "operation"},
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dtos.ts.j2",
                    "output": ["models", "dtos.ts"],
                    "provides": ["dtos"],
                },
                "operations": {
                    "selection": "operations",
                    "template": "operation.ts.j2",
                    "output": ["operations", "[operation.name].ts"],
                    "imports": {"dtos": "dto-types"},
                },
            },
        },
        strict=True,
    )

    plan = plan_path_graph(
        config=config,
        base_context={"dtos": dtos, "operations": (operation,)},
        template_root=tmp_path,
    )

    aggregate = plan.registry.find_emission("dto-types")[0]
    assert aggregate.refs == (first_ref, second_ref)
    operation_file = next(file for file in plan.files if file.node_key == "operations")
    assert operation_file.depends_on == ("models/dtos.ts",)


def test_graph_rejects_effective_provider_overlap(tmp_path: Path) -> None:
    _templates(tmp_path, "dto.ts.j2", "index.ts.j2", "operation.ts.j2")
    dto_ref = "#/components/schemas/CreateUserDto"
    dto = _item("CreateUserDto", "dto:create", dto_ref)
    operation = _item(
        "createUser",
        "operation:create",
        "#/paths/~1users/post",
        dependencies=(FakeDependency(dto_ref),),
    )
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "dtos", "as": "dto"},
                "operations": {"select": "operations", "as": "operation"},
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", "[dto.name].ts"],
                    "provides": ["dtos"],
                },
                "operations": {
                    "selection": "operations",
                    "template": "operation.ts.j2",
                    "output": ["operations", "[operation.name].ts"],
                    "imports": {
                        "dtos": "dto-types",
                        "enums": "models-barrel",
                    },
                },
            },
            "barrels": {
                "models-barrel": {
                    "template": "index.ts.j2",
                    "output": ["models", "index.ts"],
                    "exports": ["dto-types"],
                }
            },
        },
        strict=True,
    )

    with pytest.raises(PathGraphPlanningError, match="overlapping providers"):
        plan_path_graph(
            config=config,
            base_context={"dtos": (dto,), "operations": (operation,)},
            template_root=tmp_path,
        )


def test_graph_scopes_barrels_to_resource_members(tmp_path: Path) -> None:
    _templates(tmp_path, "dto.ts.j2", "index.ts.j2")
    dtos = (
        _item("UserDto", "dto:user", "#/components/schemas/UserDto", resource="users"),
        _item("OrderDto", "dto:order", "#/components/schemas/OrderDto", resource="orders"),
    )
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "dtos", "as": "dto"},
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", "[dto.resource]", "[dto.name].ts"],
                    "provides": ["dtos"],
                },
            },
            "barrels": {
                "resource-models": {
                    "template": "index.ts.j2",
                    "output": ["models", "[barrel.resource]", "index.ts"],
                    "exports": ["dto-types"],
                    "scope": "resource",
                }
            },
        },
        strict=True,
    )

    plan = plan_path_graph(
        config=config,
        base_context={"dtos": dtos},
        template_root=tmp_path,
    )

    barrels = [file for file in plan.files if file.is_barrel]
    assert [file.output_path.as_posix() for file in barrels] == [
        "models/orders/index.ts",
        "models/users/index.ts",
    ]
    assert barrels[0].depends_on == ("models/orders/OrderDto.ts",)
    assert barrels[1].depends_on == ("models/users/UserDto.ts",)


def test_graph_requires_provider_for_importable_dependencies(tmp_path: Path) -> None:
    _templates(tmp_path, "operation.ts.j2")
    operation = _item(
        "createUser",
        "operation:create",
        "#/paths/~1users/post",
        dependencies=(FakeDependency("#/components/schemas/CreateUserDto"),),
    )
    config = path_config_from_yaml(
        {
            "selections": {
                "operations": {"select": "operations", "as": "operation"},
            },
            "emissions": {
                "operations": {
                    "selection": "operations",
                    "template": "operation.ts.j2",
                    "output": ["operations", "[operation.name].ts"],
                },
            },
        },
        strict=True,
    )

    with pytest.raises(PathGraphPlanningError, match="declares no providers"):
        plan_path_graph(
            config=config,
            base_context={"operations": (operation,)},
            template_root=tmp_path,
        )


def _item(
    name: str,
    key: str,
    ref: str,
    *,
    dependencies: tuple[FakeDependency, ...] = (),
    resource: str | None = None,
) -> FakeItem:
    return FakeItem(
        name=name,
        emit=FakeEmit(
            key=key,
            ref=ref,
            dependencies=dependencies,
            resource_path=(resource,) if resource else (),
        ),
        lang=FakeLang(symbol_name=name),
        resource=resource,
    )


def _templates(root: Path, *names: str) -> None:
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{{ file.name if file is defined else 'planned' }}\n", encoding="utf-8")
