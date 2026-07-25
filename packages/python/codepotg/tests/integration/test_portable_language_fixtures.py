"""Executable Jinja fixture coverage for portable language adapters."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app import GeneratorApp

LANGUAGES = ("python", "java", "csharp", "go", "rust")


@pytest.mark.parametrize("language", LANGUAGES)
def test_portable_language_fixture_emits_complete_variable_probe(
    tmp_path: Path,
    language: str,
) -> None:
    fixture_root = Path(__file__).resolve().parents[1] / "fixtures" / "portable_languages"
    workspace = Path(shutil.copytree(fixture_root, tmp_path / "portable_languages"))
    config = workspace / language / "Codepotg.yml"

    first = GeneratorApp().generate(config_path=config, task_name="fixture")
    second = GeneratorApp().generate(config_path=config, task_name="fixture")

    first_task = first.tasks[0]
    second_task = second.tasks[0]
    assert first_task.language == language
    assert len(first_task.planned) >= 5
    assert len(first_task.written) == len(first_task.planned)
    assert len(set(first_task.planned)) == len(first_task.planned)
    assert first_task.refused == []
    assert all(path.is_file() for path in first_task.written)

    assert second_task.written == []
    assert len(second_task.unchanged) == len(first_task.planned)
    assert any(
        "JSONL cache reused" in diagnostic.message
        for diagnostic in second_task.diagnostics
    )

    output = workspace / language / ".generated-review"
    global_probe = (output / "contract" / "variables.txt").read_text(encoding="utf-8")
    expected = {
        f"language={language}",
        "complete_contract=True",
        "api_title=Portable Contract API",
        "openapi_version=3.1.0",
        "api_version=v1",
        "server_url=https://portable.example.test/v1",
        "raw_openapi=3.1.0",
        "raw_title=Portable Contract API",
        "lossless_extension=lossless",
        "operation_count=1",
        "resource_count=1",
    }
    for marker in expected:
        assert marker in global_probe

    schema_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (output / "schemas").glob("*.txt")
    )
    assert "selection=schema" in schema_text
    assert "name=Widget" in schema_text
    assert "name=WidgetStatus" in schema_text
    assert "raw_probe=widget" in schema_text
    assert "raw_probe=status" in schema_text

    operation_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (output / "operations").glob("*.txt")
    )
    assert "selection=operation" in operation_text
    assert "name=listWidgets" in operation_text
    assert "method=get" in operation_text
    assert "path=/widgets" in operation_text

    resource_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (output / "resources").glob("*.txt")
    )
    assert "selection=resource" in resource_text
    assert "name=Widgets" in resource_text
    assert "operation_count=1" in resource_text
