"""End-to-end proof for the approved paths.yaml selection graph."""

from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp


def test_complete_paths_graph_fixture(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "fixtures" / "graph_contract"
    project = Path(shutil.copytree(source, tmp_path / "graph_contract"))
    config = project / "Codepotg.yml"

    first = GeneratorApp().generate(config_path=config, task_name="graph")
    second = GeneratorApp().generate(config_path=config, task_name="graph")

    first_task = first.tasks[0]
    second_task = second.tasks[0]
    assert first_task.language == "python"
    assert len(first_task.planned) >= 10
    assert len(first_task.written) == len(first_task.planned)
    assert len(set(first_task.planned)) == len(first_task.planned)
    assert first_task.refused == []
    assert all(path.is_file() for path in first_task.written)

    assert second_task.written == []
    assert second_task.updated == []
    assert len(second_task.unchanged) + len(second_task.immutable_skipped) == len(
        first_task.planned
    )
    assert len(second_task.immutable_skipped) == 1
    assert second_task.immutable_skipped[0].name == "schemas.txt"
    assert any(
        "JSONL cache reused" in diagnostic.message
        for diagnostic in second_task.diagnostics
    )

    output = project / ".generated-review" / "generated"
    model = _one((output / "models").glob("widget.txt")).read_text(encoding="utf-8")
    audit = _one((output / "audits").glob("widget.txt")).read_text(encoding="utf-8")
    operation_files = tuple((output / "operations").glob("*.txt"))
    operation_text = "\n".join(path.read_text(encoding="utf-8") for path in operation_files)
    resource_text = _one(output.glob("resources/*/operations.txt")).read_text(
        encoding="utf-8"
    )
    inventory = (output / "schema-inventory.txt").read_text(encoding="utf-8")
    barrel = (output / "barrels" / "schemas.txt").read_text(encoding="utf-8")

    assert "node=model-types" in model
    assert "selection=models" in model
    assert "source_ref=#/components/schemas/Widget" in model
    assert "provider=enum-types" in model
    assert "document_openapi=3.1.0" in model
    assert "resolver_loads=" in model

    assert "node=model-audit" in audit
    assert "source_ref=#/components/schemas/Widget" in audit
    assert len(operation_files) == 2
    assert "operation=listWidgets" in operation_text
    assert "operation=createWidget" in operation_text
    assert "provider_models=model-types" in operation_text
    assert "provider_dtos=dto-types" in operation_text
    assert "provider_enums=enum-types" in operation_text
    assert "resolved_operation=operation:" in operation_text

    assert "scope=resource" in resource_text
    assert "count=2" in resource_text
    assert "listWidgets" in resource_text
    assert "createWidget" in resource_text

    assert "scope=all" in inventory
    assert "Widget" in inventory
    assert "WidgetStatus" in inventory
    assert "CreateWidgetDto" in inventory
    assert "document_extension=complete" in inventory

    assert "barrel=schema-barrel" in barrel
    assert "scope=all" in barrel
    assert "models" in barrel
    assert "enums" in barrel
    assert "generated/models/widget.txt" in barrel
    assert "generated/enums/widget_status.txt" in barrel


def _one(values) -> Path:
    items = tuple(values)
    assert len(items) == 1, [str(item) for item in items]
    return items[0]
