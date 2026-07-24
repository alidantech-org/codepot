from __future__ import annotations

from pathlib import Path

import pytest

from codepot_file.loader import load_codepotg_config, resolve_codepotg_config
from core.errors import ConfigError


CONFIG_BODY = """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
""".strip()


def test_missing_config_file_fails_with_helpful_message(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="Codepotg.yaml or Codepotg.yml not found"):
        resolve_codepotg_config()


@pytest.mark.parametrize("config_name", ["Codepotg.yaml", "Codepotg.yml"])
def test_codepotg_yaml_extensions_load_the_same_config(
    tmp_path: Path,
    config_name: str,
) -> None:
    config = tmp_path / config_name
    config.write_text(CONFIG_BODY, encoding="utf-8")

    loaded = load_codepotg_config(config)

    assert loaded.path == config.resolve()
    assert loaded.allow is True
    assert loaded.tasks[0].name == "sdk"
    assert loaded.tasks[0].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[0].template_dir == (tmp_path / "templates").resolve()
    assert loaded.tasks[0].output == (tmp_path / "lib").resolve()
    assert loaded.tasks[0].frontend is None


@pytest.mark.parametrize("config_name", ["Codepotg.yaml", "Codepotg.yml"])
def test_default_discovery_supports_both_yaml_extensions(
    tmp_path: Path,
    monkeypatch,
    config_name: str,
) -> None:
    config = tmp_path / config_name
    config.write_text(CONFIG_BODY, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert resolve_codepotg_config() == config.resolve()


def test_default_discovery_rejects_ambiguous_yaml_and_yml_configs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "Codepotg.yaml").write_text(CONFIG_BODY, encoding="utf-8")
    (tmp_path / "Codepotg.yml").write_text(CONFIG_BODY, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="Multiple CodepotG configs found"):
        resolve_codepotg_config()


def test_bundled_templates_are_selected_when_template_path_is_omitted(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yaml"
    config.write_text(
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    output: ./lib
""".strip(),
        encoding="utf-8",
    )

    task = load_codepotg_config(config).tasks[0]

    assert task.template_dir is None


def test_task_frontend_option_is_parsed(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yml"
    config.write_text(
        """
allow: true
tasks:
  admin-frontend:
    input: ./openapi.yaml
    language: typescript
    output: ./admin
    frontend: admin
""".strip(),
        encoding="utf-8",
    )

    task = load_codepotg_config(config).tasks[0]

    assert task.frontend == "admin"


def test_templates_alias_loading_parses_custom_path(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yaml"
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

    loaded = load_codepotg_config(config)

    assert loaded.tasks[0].language == "dart"
    assert loaded.tasks[0].template_dir == (tmp_path / "templates").resolve()


@pytest.mark.parametrize("legacy_name", ["CodepotFile.yml", "CodepotFile.yaml"])
def test_legacy_codepot_file_names_are_rejected(
    tmp_path: Path,
    monkeypatch,
    legacy_name: str,
) -> None:
    (tmp_path / legacy_name).write_text("allow: true\ntasks: {}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="CodepotG uses Codepotg.yaml or Codepotg.yml"):
        resolve_codepotg_config()


def test_relative_paths_resolve_from_config_directory(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = project / "Codepotg.yml"
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

    task = load_codepotg_config(config).tasks[0]

    assert task.input == (tmp_path / "backend" / "openapi.yaml").resolve()
    assert task.template_dir == (tmp_path / "backend" / "templates").resolve()
    assert task.output == (project / "lib").resolve()
    assert task.before[0].cwd == (tmp_path / "backend").resolve()


def test_defaults_are_merged_into_tasks(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yaml"
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
    output: ./admin
  mobile:
    language: dart
    output: ./mobile
""".strip(),
        encoding="utf-8",
    )

    loaded = load_codepotg_config(config)

    assert loaded.tasks[0].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[1].input == (tmp_path / "openapi.yaml").resolve()
    assert loaded.tasks[0].before[0].run == "echo before"
    assert loaded.tasks[0].template_dir is None
    assert loaded.tasks[1].template_dir is None


def test_task_list_fields_override_defaults_without_concatenation(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yml"
    config.write_text(
        """
allow: true
defaults:
  input: ./openapi.yaml
  language: typescript
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

    task = load_codepotg_config(config).tasks[0]

    assert [command.run for command in task.after] == ["echo task"]
