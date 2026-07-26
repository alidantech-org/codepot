"""Executable Jinja and native artifact coverage for production adapters."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app import GeneratorApp

LANGUAGES = ("python", "java", "csharp", "go", "rust")
TARGETS = {
    "python": {
        "extension": ".py",
        "manifest": "pyproject.toml",
        "model_parts": ("package", "src", "portable_client", "models"),
        "client_parts": ("package", "src", "portable_client", "client"),
        "model": "class Widget(BaseModel):",
        "uuid": "uuid.UUID",
        "operation": "def list_widgets(",
    },
    "java": {
        "extension": ".java",
        "manifest": "pom.xml",
        "model_parts": (
            "package",
            "src",
            "main",
            "java",
            "generated",
            "models",
        ),
        "client_parts": (
            "package",
            "src",
            "main",
            "java",
            "generated",
            "client",
        ),
        "model": "public record Widget(",
        "uuid": "UUID id",
        "operation": "public final class ListWidgetsClient",
    },
    "csharp": {
        "extension": ".cs",
        "manifest": "GeneratedClient.csproj",
        "model_parts": ("package", "Models"),
        "client_parts": ("package", "Client"),
        "model": "public sealed record Widget",
        "uuid": "Guid Id",
        "operation": "public static class ListWidgetsClient",
    },
    "go": {
        "extension": ".go",
        "manifest": "go.mod",
        "model_parts": ("package", "models"),
        "client_parts": ("package", "client"),
        "model": "type Widget struct {",
        "uuid": "Id uuid.UUID",
        "operation": "const ListWidgetsMethod",
    },
    "rust": {
        "extension": ".rs",
        "manifest": "Cargo.toml",
        "model_parts": ("package", "src", "models"),
        "client_parts": ("package", "src", "client"),
        "model": "pub struct Widget {",
        "uuid": "pub id: uuid::Uuid",
        "operation": "pub async fn list_widgets()",
    },
}


@pytest.mark.parametrize("language", LANGUAGES)
def test_portable_language_fixture_emits_complete_contract_and_native_package(
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
    assert len(first_task.planned) >= 9
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
    global_probe = (output / "contract" / "variables.txt").read_text(
        encoding="utf-8"
    )
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

    target = TARGETS[language]
    model_root = output.joinpath(*target["model_parts"])
    client_root = output.joinpath(*target["client_parts"])
    manifest = output / "package" / target["manifest"]
    model = model_root / f"widget{target['extension']}"
    enum = model_root / f"widget_status{target['extension']}"
    operation = client_root / f"list_widgets_client{target['extension']}"

    assert manifest.is_file()
    assert model.is_file()
    assert enum.is_file()
    assert operation.is_file()

    model_text = model.read_text(encoding="utf-8")
    assert target["model"] in model_text
    assert target["uuid"] in model_text
    assert "WidgetStatus" in model_text

    enum_text = enum.read_text(encoding="utf-8")
    assert "WidgetStatus" in enum_text
    assert "active" in enum_text.lower()
    assert "disabled" in enum_text.lower()

    operation_source = operation.read_text(encoding="utf-8")
    assert target["operation"] in operation_source
    assert "/widgets" in operation_source
