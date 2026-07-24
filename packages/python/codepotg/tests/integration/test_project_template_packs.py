from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest

from app import GeneratorApp


@dataclass(frozen=True)
class ProjectCase:
    folder: str
    config_name: str
    language: str
    extension: str
    project_title_line: str
    language_line: str


CASES = (
    ProjectCase(
        folder="typescript",
        config_name="Codepotg.yml",
        language="typescript",
        extension="ts",
        project_title_line='apiTitle: "CodepotG Fixture API"',
        language_line='language: "typescript"',
    ),
    ProjectCase(
        folder="dart",
        config_name="Codepotg.yaml",
        language="dart",
        extension="dart",
        project_title_line="'apiTitle': 'CodepotG Fixture API'",
        language_line="'language': 'dart'",
    ),
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.language)
def test_real_project_fixture_generates_custom_template_pack(
    tmp_path: Path,
    case: ProjectCase,
) -> None:
    project = _copy_project_fixture(tmp_path, case)
    config = project / case.config_name

    assert not (project / ".generated").exists()
    assert not (project / ".codepotg").exists()

    result = GeneratorApp().generate(config_path=config, task_name="fixture")

    assert result.config_path == config.resolve()
    assert result.dry_run is False
    assert len(result.tasks) == 1

    task = result.tasks[0]
    assert task.name == "fixture"
    assert task.language == case.language
    assert task.output_path == (project / ".generated").resolve()
    assert task.template_dir == (project / "templates").resolve()
    assert len(task.planned) == 9
    assert len(task.written) == 9
    assert task.refused == []

    cache = project / ".codepotg" / "cache" / "openapi"
    assert (cache / "manifest.json").is_file()
    assert (cache / "paths.jsonl").is_file()
    assert (cache / "components" / "schemas.jsonl").is_file()
    manifest = json.loads((cache / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"]["format"] == "yaml"
    assert manifest["source"]["compiledFormat"] == "json"
    assert any("JSONL cache" in diagnostic.message for diagnostic in task.diagnostics)

    output = project / ".generated"
    expected = _expected_output_files(output, case.extension)
    assert {path.resolve() for path in task.written} == {path.resolve() for path in expected}
    assert all(path.is_file() for path in expected)

    project_content = (output / "contract" / f"project.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert case.project_title_line in project_content
    assert case.language_line in project_content
    assert "resourceCount" in project_content
    assert "schemaCount" in project_content
    assert "operationCount" in project_content

    source_content = (output / "contract" / f"source.{case.extension}").read_text(
        encoding="utf-8"
    )
    for expected_source_value in (
        "3.1.0",
        "CodepotG Fixture API",
        "listUsers",
        "codepotg",
        "first",
        "second",
        "True",
    ):
        assert expected_source_value in source_content

    collections = (output / "contract" / f"collections.{case.extension}").read_text(
        encoding="utf-8"
    )
    for expected_name in (
        "UserModel",
        "CreateUserBody",
        "UserStatus",
        "listUsers",
        "createUser",
    ):
        assert expected_name in collections

    user_schema = (output / "schemas" / f"user_model.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "UserModel" in user_schema
    assert "fieldCount" in user_schema
    assert "age" in user_schema
    assert "18" in user_schema

    list_operation = (output / "operations" / f"list_users.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "listUsers" in list_operation
    assert "parameterCount" in list_operation
    assert "1" in list_operation

    create_operation = (output / "operations" / f"create_user.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "createUser" in create_operation
    assert "hasRequestBody" in create_operation
    assert "True" in create_operation

    resource = (output / "resources" / f"users.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "Users" in resource
    assert "operationCount" in resource
    assert "schemaCount" in resource


@pytest.mark.parametrize("case", CASES, ids=lambda case: f"discover-{case.language}")
def test_real_project_fixture_is_discovered_by_standard_config_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: ProjectCase,
) -> None:
    project = _copy_project_fixture(tmp_path, case)
    monkeypatch.chdir(project)

    assert not (project / ".generated").exists()
    assert not (project / ".codepotg").exists()

    result = GeneratorApp().generate(task_name="fixture")

    assert result.config_path == (project / case.config_name).resolve()
    assert result.tasks[0].language == case.language
    assert len(result.tasks[0].written) == 9
    assert (project / ".codepotg" / "cache" / "openapi" / "manifest.json").is_file()


def test_generation_reuses_unchanged_jsonl_cache(tmp_path: Path) -> None:
    case = CASES[0]
    project = _copy_project_fixture(tmp_path, case)
    config = project / case.config_name

    first = GeneratorApp().generate(config_path=config, task_name="fixture")
    second = GeneratorApp().generate(config_path=config, task_name="fixture")

    assert len(first.tasks[0].written) == 9
    assert second.tasks[0].written == []
    assert len(second.tasks[0].unchanged) == 9
    assert any(
        "JSONL cache reused" in diagnostic.message
        for diagnostic in second.tasks[0].diagnostics
    )


def test_fixture_output_directories_are_ignored() -> None:
    fixtures = _fixtures_root()

    for case in CASES:
        ignored = (fixtures / case.folder / ".gitignore").read_text(
            encoding="utf-8"
        ).splitlines()
        assert ".generated/" in ignored
        assert ".codepotg/" in ignored


def _copy_project_fixture(tmp_path: Path, case: ProjectCase) -> Path:
    source = _fixtures_root() / case.folder
    target = tmp_path / case.folder
    return Path(
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(".generated", ".codepotg"),
        )
    )


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"


def _expected_output_files(output: Path, extension: str) -> tuple[Path, ...]:
    return (
        output / "contract" / f"project.{extension}",
        output / "contract" / f"collections.{extension}",
        output / "contract" / f"source.{extension}",
        output / "schemas" / f"user_status.{extension}",
        output / "schemas" / f"user_model.{extension}",
        output / "schemas" / f"create_user_body.{extension}",
        output / "operations" / f"list_users.{extension}",
        output / "operations" / f"create_user.{extension}",
        output / "resources" / f"users.{extension}",
    )
