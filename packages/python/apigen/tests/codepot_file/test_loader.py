from __future__ import annotations

from pathlib import Path

import pytest

from codepot_file.loader import load_codepot_file, resolve_codepot_file
from core.errors import ConfigError


def test_missing_config_file_fails_with_helpful_message(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="CodepotFile.yml not found"):
        resolve_codepot_file()


def test_codepot_file_yml_loading_parses_yaml(tmp_path: Path) -> None:
    config = tmp_path / "CodepotFile.yml"
    config.write_text(
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
""".strip(),
        encoding="utf-8",
    )

    loaded = load_codepot_file(config)

    assert loaded.allow is True
    assert loaded.tasks[0].name == "sdk"
    assert loaded.tasks[0].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[0].template_dir == (tmp_path / "templates").resolve()
    assert loaded.tasks[0].output == (tmp_path / "lib").resolve()


def test_codepot_file_yaml_loading_parses_yaml(tmp_path: Path) -> None:
    config = tmp_path / "CodepotFile.yaml"
    config.write_text(
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: dart
    templates: ./templates
    output: ./pkg/api
""".strip(),
        encoding="utf-8",
    )

    loaded = load_codepot_file(config)

    assert loaded.tasks[0].language == "dart"
    assert loaded.tasks[0].template_dir == (tmp_path / "templates").resolve()


def test_both_config_files_present_fails_with_conflict(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "CodepotFile.yml").write_text("allow: true\ntasks: {}\n", encoding="utf-8")
    (tmp_path / "CodepotFile.yaml").write_text("allow: true\ntasks: {}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="Multiple CodepotFile configs found"):
        resolve_codepot_file()


def test_relative_paths_resolve_from_config_directory(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = project / "CodepotFile.yml"
    config.write_text(
        """
allow: true
tasks:
  sdk:
    input: ../backend/openapi.yaml
    language: typescript
    templateDir: ../backend/templates
    output: ./lib
    before:
      - cwd: ../backend
        run: echo before
""".strip(),
        encoding="utf-8",
    )

    task = load_codepot_file(config).tasks[0]

    assert task.input == (tmp_path / "backend" / "openapi.yaml").resolve()
    assert task.template_dir == (tmp_path / "backend" / "templates").resolve()
    assert task.output == (project / "lib").resolve()
    assert task.before[0].cwd == (tmp_path / "backend").resolve()


def test_defaults_are_merged_into_tasks(tmp_path: Path) -> None:
    config = tmp_path / "CodepotFile.yml"
    config.write_text(
        """
allow: true
defaults:
  input: ./openapi.yaml
  before:
    - run: echo before
tasks:
  admin:
    language: typescript
    templateDir: ./templates
    output: ./admin
  mobile:
    language: dart
    templateDir: ./dart
    output: ./mobile
""".strip(),
        encoding="utf-8",
    )

    loaded = load_codepot_file(config)

    assert loaded.tasks[0].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[1].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[0].before[0].run == "echo before"


def test_task_list_fields_override_defaults_without_concatenation(tmp_path: Path) -> None:
    config = tmp_path / "CodepotFile.yml"
    config.write_text(
        """
allow: true
defaults:
  input: ./openapi.yaml
  language: typescript
  templateDir: ./templates
  output: ./lib
  after:
    - run: echo default
tasks:
  sdk:
    after:
      - run: echo task
""".strip(),
        encoding="utf-8",
    )

    task = load_codepot_file(config).tasks[0]

    assert [command.run for command in task.after] == ["echo task"]
