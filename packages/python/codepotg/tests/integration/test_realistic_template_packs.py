from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
from archives.codepotg.tests.fixtures.realistic_openapi import (
    FICTIONAL_SERVER_URL,
    write_fictional_real_openapi,
)

from app import GeneratorApp


@dataclass(frozen=True)
class RealisticPackCase:
    folder: str
    config_name: str
    language: str
    minimum_outputs: int
    enum_pattern: str
    normalized_markers: tuple[str, ...]


CASES = (
    RealisticPackCase(
        folder="nest_backend",
        config_name="Codepotg.yml",
        language="typescript",
        minimum_outputs=250,
        enum_pattern="app-status.ts",
        normalized_markers=("Normalized schema: AppStatus",),
    ),
    RealisticPackCase(
        folder="next_server_actions",
        config_name="Codepotg.yml",
        language="typescript",
        minimum_outputs=100,
        enum_pattern="app-status.ts",
        normalized_markers=("Normalized schema: AppStatus",),
    ),
    RealisticPackCase(
        folder="dart_client",
        config_name="Codepotg.yaml",
        language="dart",
        minimum_outputs=150,
        enum_pattern="enum.dart",
        normalized_markers=("Normalized schema: AppStatus",),
    ),
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.folder)
def test_large_real_contract_generates_realistic_pack(
    tmp_path: Path,
    real_openapi_json_path: Path,
    case: RealisticPackCase,
) -> None:
    project = _copy_project(tmp_path, case)
    input_path = write_fictional_real_openapi(
        real_openapi_json_path,
        project / "openapi.generated.json",
    )
    document = json.loads(input_path.read_text(encoding="utf-8"))
    assert input_path.stat().st_size > 500_000
    assert len(document["paths"]) >= 100
    assert len(document["components"]["schemas"]) >= 100

    result = GeneratorApp().generate(
        config_path=project / case.config_name,
        task_name="realistic",
    )
    task = result.tasks[0]

    assert task.language == case.language
    assert len(task.planned) >= case.minimum_outputs
    assert len(task.written) == len(task.planned)
    assert len(set(task.planned)) == len(task.planned)
    assert task.updated == []
    assert task.unchanged == []
    assert task.refused == []
    assert all(path.is_file() for path in task.written)
    assert any(
        "SQLite" in diagnostic.message or "sqlite" in diagnostic.message
        for diagnostic in task.diagnostics
    )
    assert any("Normalized roots:" in diagnostic.message for diagnostic in task.diagnostics)

    output = project / ".generated-review"
    enum_file = _app_status_file(output, case)
    enum_content = enum_file.read_text(encoding="utf-8")
    for marker in case.normalized_markers:
        assert marker in enum_content
    for value in ("active", "suspended", "disabled"):
        assert value in enum_content
    _assert_representative_example(project, enum_content)

    all_text = _representative_output_text(output)
    assert "Alidantech" not in all_text
    assert "Riderescue" not in all_text

    if case.folder == "nest_backend":
        entity = _one(output.rglob("app.entity.ts"))
        content = entity.read_text(encoding="utf-8")
        assert "Normalized store: apps" in content
        assert "Effective fields:" in content
        assert (
            output / ".gen" / "backend" / "platform" / "apps" / "entities" / "index.ts"
        ).is_file()
        assert (
            output / "src" / "modules" / "platform" / "apps" / "use-cases" / "index.ts"
        ).is_file()
    elif case.folder == "next_server_actions":
        actions = _one(output.rglob("apps.actions.ts"))
        content = actions.read_text(encoding="utf-8")
        assert "Base route: /platform/apps" in content
        assert FICTIONAL_SERVER_URL in all_text
    else:
        feature = _one(output.rglob("apps_feature.dart"))
        assert "Resource route: /platform/apps" in feature.read_text(encoding="utf-8")
        assert "northstar" in all_text.lower()


def test_realistic_next_pack_reuses_cache_and_outputs(
    tmp_path: Path,
    real_openapi_json_path: Path,
) -> None:
    case = next(item for item in CASES if item.folder == "next_server_actions")
    project = _copy_project(tmp_path, case)
    write_fictional_real_openapi(
        real_openapi_json_path,
        project / "openapi.generated.json",
    )
    config = project / case.config_name

    first = GeneratorApp().generate(config_path=config, task_name="realistic")
    second = GeneratorApp().generate(config_path=config, task_name="realistic")

    assert len(first.tasks[0].written) >= case.minimum_outputs
    assert second.tasks[0].written == []
    assert (
        len(second.tasks[0].unchanged) + len(second.tasks[0].immutable_skipped)
        == len(first.tasks[0].planned)
    )
    assert set(second.tasks[0].unchanged).isdisjoint(
        second.tasks[0].immutable_skipped
    )
    assert all(path.is_file() for path in second.tasks[0].immutable_skipped)
    assert any(
        "JSONL cache reused" in diagnostic.message
        for diagnostic in second.tasks[0].diagnostics
    )


def test_realistic_fixture_projects_are_generic_and_reviewable() -> None:
    root = _fixtures_root()
    forbidden = (
        "Alidantech",
        "Riderescue",
        "SierreTechnologies",
        "Sierre Technologies",
    )

    for case in CASES:
        project = root / case.folder
        assert (project / case.config_name).is_file()
        assert (project / "README.md").is_file()
        assert (project / "generated-examples").is_dir()
        templates = tuple((project / "templates").rglob("*"))
        assert len(tuple(path for path in templates if path.is_file())) >= 10
        text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in templates
            if path.is_file()
        )
        for value in forbidden:
            assert value not in text


def _copy_project(tmp_path: Path, case: RealisticPackCase) -> Path:
    return Path(
        shutil.copytree(
            _fixtures_root() / case.folder,
            tmp_path / case.folder,
            ignore=shutil.ignore_patterns(
                ".generated-review",
                ".codepotg",
                "openapi.generated.json",
            ),
        )
    )


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "realistic_projects"


def _app_status_file(output: Path, case: RealisticPackCase) -> Path:
    candidates = tuple(output.rglob(case.enum_pattern))
    candidates = tuple(
        path
        for path in candidates
        if "app-status" in path.as_posix() or "app_status" in path.as_posix()
    )
    return _one(candidates)


def _assert_representative_example(project: Path, generated: str) -> None:
    example = _one((project / "generated-examples").iterdir())
    lines = [
        line.strip()
        for line in example.read_text(encoding="utf-8").splitlines()
        if line.strip()
        and not line.lstrip().startswith(("//", "/*", "*"))
    ]
    for line in lines:
        assert line in generated


def _representative_output_text(output: Path) -> str:
    names = {
        "README.md",
        "pubspec.yaml",
        "api.ts",
        "routes.ts",
        "v1.ts",
        "v1.dart",
    }
    files = [
        path
        for path in output.rglob("*")
        if path.is_file() and path.name in names
    ]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in files
    )


def _one(values) -> Path:
    items = tuple(values)
    assert len(items) == 1, [str(item) for item in items]
    return items[0]
