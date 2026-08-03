"""Package and module entry-point coverage for portable language fixtures."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app import GeneratorApp

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "portable_languages"
SUPPORT_FILES = {
    "python": {
        "src/portable_client/__init__.py": "Generated portable API client package",
        "src/portable_client/models/__init__.py": "WidgetListResponse",
        "src/portable_client/client/__init__.py": "list_widgets",
    },
    "java": {
        "src/main/java/generated/models/package-info.java": "package generated.models;",
        "src/main/java/generated/client/package-info.java": "package generated.client;",
    },
    "csharp": {
        "GlobalUsings.cs": "global using System.Collections.Generic;",
    },
    "go": {
        "models/doc.go": "package models",
        "client/doc.go": "package client",
    },
    "rust": {
        "src/lib.rs": "pub mod models;",
        "src/models/mod.rs": "pub mod widget_list_response;",
        "src/client/mod.rs": '#[path = "ListWidgetsClient.rs"]',
    },
}


@pytest.mark.parametrize("language", tuple(SUPPORT_FILES))
def test_portable_fixture_emits_adapter_declared_support_files(
    tmp_path: Path,
    language: str,
) -> None:
    workspace = Path(shutil.copytree(FIXTURE_ROOT, tmp_path / "portable_languages"))
    config = workspace / language / "Codepotg.yml"

    result = GeneratorApp().generate(config_path=config, task_name="fixture")
    task = result.tasks[0]
    assert task.refused == []

    package = workspace / language / ".generated-review" / "package"
    for relative_path, marker in SUPPORT_FILES[language].items():
        path = package / relative_path
        assert path.is_file(), relative_path
        assert marker in path.read_text(encoding="utf-8")
