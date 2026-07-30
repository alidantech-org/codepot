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
        "model_file": "widget.py",
        "enum_file": "widget_status.py",
        "response_file": "widget_list_response.py",
        "client_file": "ListWidgetsClient.py",
        "model": "class Widget(BaseModel):",
        "uuid": "uuid.UUID",
        "response_field": "items: list[Widget]",
        "operation": "def list_widgets(",
        "typed_operation": "-> WidgetListResponse:",
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
        "model_file": "Widget.java",
        "enum_file": "WidgetStatus.java",
        "response_file": "WidgetListResponse.java",
        "client_file": "ListWidgetsClient.java",
        "model": "public record Widget(",
        "uuid": "UUID id",
        "response_field": "List<Widget> items",
        "operation": "public final class ListWidgetsClient",
        "typed_operation": "public static WidgetListResponse decodeResponse",
    },
    "csharp": {
        "extension": ".cs",
        "manifest": "GeneratedClient.csproj",
        "model_parts": ("package", "Models"),
        "client_parts": ("package", "Client"),
        "model_file": "Widget.cs",
        "enum_file": "WidgetStatus.cs",
        "response_file": "WidgetListResponse.cs",
        "client_file": "ListWidgetsClient.cs",
        "model": "public sealed record Widget",
        "uuid": "Guid Id",
        "response_field": "List<Widget> Items",
        "operation": "public static class ListWidgetsClient",
        "typed_operation": "public static WidgetListResponse DecodeResponse",
    },
    "go": {
        "extension": ".go",
        "manifest": "go.mod",
        "model_parts": ("package", "models"),
        "client_parts": ("package", "client"),
        "model_file": "widget.go",
        "enum_file": "widget_status.go",
        "response_file": "widget_list_response.go",
        "client_file": "ListWidgetsClient.go",
        "model": "type Widget struct {",
        "uuid": "Id uuid.UUID",
        "response_field": "Items []Widget",
        "operation": "const ListWidgetsMethod",
        "typed_operation": "(models.WidgetListResponse, error)",
    },
    "rust": {
        "extension": ".rs",
        "manifest": "Cargo.toml",
        "model_parts": ("package", "src", "models"),
        "client_parts": ("package", "src", "client"),
        "model_file": "widget.rs",
        "enum_file": "widget_status.rs",
        "response_file": "widget_list_response.rs",
        "client_file": "ListWidgetsClient.rs",
        "model": "pub struct Widget {",
        "uuid": "pub id: uuid::Uuid",
        "response_field": "pub items: Vec<Widget>",
        "operation": "pub async fn list_widgets()",
        "typed_operation": "Result<WidgetListResponse, reqwest::Error>",
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
    assert len(first_task.planned) >= 10
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
    assert "name=WidgetListResponse" in schema_text
    assert "raw_probe=widget" in schema_text
    assert "raw_probe=status" in schema_text
    assert "raw_probe=widget-list-response" in schema_text

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
    model = model_root / target["model_file"]
    enum = model_root / target["enum_file"]
    response_model = model_root / target["response_file"]
    operation = client_root / target["client_file"]

    assert manifest.is_file()
    assert model.is_file()
    assert enum.is_file()
    assert response_model.is_file()
    assert operation.is_file()

    model_text = model.read_text(encoding="utf-8")
    assert target["model"] in model_text
    assert target["uuid"] in model_text
    assert "WidgetStatus" in model_text

    enum_text = enum.read_text(encoding="utf-8")
    assert "WidgetStatus" in enum_text
    assert "active" in enum_text.lower()
    assert "disabled" in enum_text.lower()

    response_text = response_model.read_text(encoding="utf-8")
    assert "WidgetListResponse" in response_text
    assert target["response_field"] in response_text

    operation_source = operation.read_text(encoding="utf-8")
    assert target["operation"] in operation_source
    assert target["typed_operation"] in operation_source
    assert "/widgets" in operation_source
