from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contracts.normalized import SourceObject
from contracts.path_yaml import path_config_from_yaml
from contracts.template import TemplateDependency
from emission.graph_engine import _emission_file
from emission.imports.planner import RelativeImportPlanner
from emission.paths.graph_planner import plan_path_graph


@dataclass(frozen=True)
class FakeEmit:
    key: str
    ref: str
    dependencies: tuple[TemplateDependency, ...] = ()
    resource_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class FakeLang:
    symbol_name: str


@dataclass(frozen=True)
class FakeSchema:
    name: str
    emit: FakeEmit
    lang: FakeLang
    source: SourceObject = SourceObject()


def test_same_emission_can_provide_sibling_outputs_without_node_cycle(
    tmp_path: Path,
) -> None:
    model_b = FakeSchema(
        name="ModelB",
        emit=FakeEmit(key="schema:ModelB", ref="#/components/schemas/ModelB"),
        lang=FakeLang(symbol_name="ModelB"),
    )
    model_a = FakeSchema(
        name="ModelA",
        emit=FakeEmit(
            key="schema:ModelA",
            ref="#/components/schemas/ModelA",
            dependencies=(
                TemplateDependency(ref="#/components/schemas/ModelB"),
            ),
        ),
        lang=FakeLang(symbol_name="ModelA"),
    )
    template = tmp_path / "model.ts.j2"
    template.write_text("model\n", encoding="utf-8")
    config = path_config_from_yaml(
        {
            "selections": {
                "models": {
                    "select": "schemas.emit_models",
                    "as": "schema",
                }
            },
            "emissions": {
                "model-types": {
                    "selection": "models",
                    "template": "model.ts.j2",
                    "output": ["models", "[schema.name].ts"],
                    "provides": ["models"],
                    "imports": {"models": "model-types"},
                }
            },
        },
        strict=True,
    )
    graph = plan_path_graph(
        config=config,
        base_context={
            "schemas": type("Schemas", (), {"emit_models": (model_a, model_b)})(),
        },
        template_root=tmp_path,
    )
    by_source = {item.output.source_key: item for item in graph.files}

    file_a = _emission_file(
        by_source["schema:ModelA"],
        registry=graph.registry,
        template_root=tmp_path,
        output_root=tmp_path / "generated",
        path_config=config,
        import_planner=RelativeImportPlanner(extension=".ts"),
        package_name=None,
    )

    assert file_a.providers == {"models": "model-types"}
    assert file_a.dependency_outputs == {
        "#/components/schemas/ModelB": "models/ModelB.ts"
    }
    assert file_a.depends_on == ()


def test_same_file_reference_is_marked_self_and_not_scheduled(tmp_path: Path) -> None:
    recursive = FakeSchema(
        name="Recursive",
        emit=FakeEmit(
            key="schema:Recursive",
            ref="#/components/schemas/Recursive",
            dependencies=(
                TemplateDependency(ref="#/components/schemas/Recursive"),
            ),
        ),
        lang=FakeLang(symbol_name="Recursive"),
    )
    (tmp_path / "model.ts.j2").write_text("model\n", encoding="utf-8")
    config = path_config_from_yaml(
        {
            "selections": {
                "models": {
                    "select": "schemas.emit_models",
                    "as": "schema",
                }
            },
            "emissions": {
                "model-types": {
                    "selection": "models",
                    "template": "model.ts.j2",
                    "output": ["models", "[schema.name].ts"],
                    "imports": {"models": "model-types"},
                }
            },
        },
        strict=True,
    )
    graph = plan_path_graph(
        config=config,
        base_context={
            "schemas": type("Schemas", (), {"emit_models": (recursive,)})(),
        },
        template_root=tmp_path,
    )
    file = _emission_file(
        graph.files[0],
        registry=graph.registry,
        template_root=tmp_path,
        output_root=tmp_path / "generated",
        path_config=config,
        import_planner=RelativeImportPlanner(extension=".ts"),
        package_name=None,
    )

    assert file.dependency_outputs == {}
    dependencies = file.context["file"].dependencies
    assert len(dependencies) == 1
    assert dependencies[0].is_self
    assert not dependencies[0].is_importable
