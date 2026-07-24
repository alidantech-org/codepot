from __future__ import annotations

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

    result = GeneratorApp().generate(config_path=config, task_name="fixture")

    assert result.config_path == config.resolve()
    assert result.dry_run is False
    assert len(result.tasks) == 1

    task = result.tasks[0]
    assert task.name == "fixture"
    assert task.language == case.language
    assert task.output_path == (project / ".generated").resolve()
    assert task.template_dir == (project / "templates").resolve()
    assert len(task.planned) == 8
    assert len(task.written) == 8
    assert task.refused == []

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

    collections = (output / "contract" / f"collections.{case.extension}").read_text(
        encoding="utf-8"
    )
    for expected_name in ("UserModel", "CreateUserBody", "UserStatus", "listUsers", "createUser"):
        assert expected_name in collections

    user_schema = (output / "schemas" / f"user-model.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "UserModel" in user_schema
    assert "fieldCount" in user_schema
    assert "age" in user_schema
    assert "18" in user_schema

    list_operation = (output / "operations" / f"list-users.{case.extension}").read_text(
        encoding="utf-8"
    )
    assert "listUsers" in list_operation
    assert "parameterCount" in list_operation
    assert "1" in list_operation

    create_operation = (output / "operations" / f"create-user.{case.extension}").read_text(
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

    result = GeneratorApp().generate(task_name="fixture")

    assert result.config_path == (project / case.config_name).resolve()
    assert result.tasks[0].language == case.language
    assert len(result.tasks[0].written) == 8


def test_fixture_output_directories_are_ignored() -> None:
    fixtures = _fixtures_root()

    for case in CASES:
        ignored = (fixtures / case.folder / ".gitignore").read_text(encoding="utf-8").splitlines()
        assert ".generated/" in ignored


def _copy_project_fixture(tmp_path: Path, case: ProjectCase) -> Path:
    source = _fixtures_root() / case.folder
    target = tmp_path / case.folder
    return Path(shutil.copytree(source, target))


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"


def _expected_output_files(output: Path, extension: str) -> tuple[Path, ...]:
    return (
        output / "contract" / f"project.{extension}",
        output / "contract" / f"collections.{extension}",
        output / "schemas" / f"user-status.{extension}",
        output / "schemas" / f"user-model.{extension}",
        output / "schemas" / f"create-user-body.{extension}",
        output / "operations" / f"list-users.{extension}",
        output / "operations" / f"create-user.{extension}",
        output / "resources" / f"users.{extension}",
    )
