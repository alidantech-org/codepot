from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from contracts.path_yaml import path_config_from_yaml
from emission.contexts.bounded import BoundedGraphContext, bounded_graph_context
from emission.paths.graph_planner import plan_path_graph
from emission.templates.resolver import resolve_variable


@dataclass(frozen=True)
class FakeEmit:
    key: str
    ref: str
    dependencies: tuple[object, ...] = ()
    resource_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class FakeLang:
    symbol_name: str


@dataclass(frozen=True)
class FakeSchema:
    name: str
    emit: FakeEmit
    lang: FakeLang


def test_bounded_context_allows_selection_without_copying_hidden_roots() -> None:
    schema = FakeSchema(
        name="UserDto",
        emit=FakeEmit(key="dto:user", ref="#/components/schemas/UserDto"),
        lang=FakeLang(symbol_name="UserDto"),
    )
    context = BoundedGraphContext(
        public={"project": "project", "lang": "typescript"},
        selection_roots={
            "api": object(),
            "schemas": SimpleNamespace(emit_dtos=(schema,)),
            "operations": (),
            "resources": (),
        },
    )

    assert resolve_variable(context, "schemas.emit_dtos") == (schema,)
    assert context["api"] is not None
    copied = dict(context)
    assert copied == {"project": "project", "lang": "typescript"}
    assert "api" not in copied
    assert "schemas" not in copied
    assert context.public_keys == ("project", "lang")
    assert context.selection_keys == ("api", "schemas", "operations", "resources")


def test_graph_planner_copies_only_bounded_globals_into_template_context(
    tmp_path: Path,
) -> None:
    schema = FakeSchema(
        name="UserDto",
        emit=FakeEmit(key="dto:user", ref="#/components/schemas/UserDto"),
        lang=FakeLang(symbol_name="UserDto"),
    )
    contract = SimpleNamespace(
        project="project",
        lang=SimpleNamespace(name="typescript"),
        emit="emit",
        meta="meta",
        selected_frontend=None,
        selected_frontends=(),
        frontend_count=0,
        api=object(),
        resources=(),
        features=(),
        schemas=SimpleNamespace(emit_dtos=(schema,)),
        operations=(),
        entities=(),
        frontends=(),
    )
    base = bounded_graph_context(contract)
    (tmp_path / "dto.ts.j2").write_text("{{ dto.name }}\n", encoding="utf-8")
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {"select": "schemas.emit_dtos", "as": "dto"}
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", "[dto.name].ts"],
                }
            },
        },
        strict=True,
    )

    graph = plan_path_graph(
        config=config,
        base_context=base,
        template_root=tmp_path,
    )

    render_context = graph.files[0].context
    assert render_context["dto"] is schema
    assert render_context["project"] == "project"
    assert "api" not in render_context
    assert "schemas" not in render_context
    assert "operations" not in render_context
    assert "resources" not in render_context
