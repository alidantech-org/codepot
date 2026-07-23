from __future__ import annotations

import sys
from pathlib import Path

import yaml
from typer.testing import CliRunner

from app.models import EmitOutput
from app.workflows import generate as generate_workflow
from cli.main import app

CONFIG_NAME = "Codepotg.yaml"


def test_generate_missing_config_file_fails_with_helpful_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["generate"])

    assert result.exit_code == 1
    assert "Codepotg.yaml not found" in result.output


def test_help_exposes_public_commands_only() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
    assert "task" in result.output
    assert "generate" in result.output
    assert "emit" not in result.output
    assert "infer" not in result.output
    assert "inspect" not in result.output
    assert "validate" not in result.output


def test_emit_command_is_not_public() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["emit", "--help"])

    assert result.exit_code != 0
    assert "No such command" in result.output


def test_task_help_exposes_add_command_only() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["task", "--help"])

    assert result.exit_code == 0
    assert "add" in result.output
    assert "emit" not in result.output


def test_init_yes_creates_minimal_starter_with_bundled_templates(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["init", "--yes"])
        config = _read_yaml(Path(CONFIG_NAME))

    assert result.exit_code == 0
    assert config == {
        "allow": True,
        "tasks": {
            "sdk": {
                "input": "./openapi.yaml",
                "language": "typescript",
                "output": "./generated",
            }
        },
    }
    assert "bundled typescript pack" in result.output


def test_init_refuses_to_overwrite_existing_config(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text("allow: true\ntasks: {}\n", encoding="utf-8")
        result = runner.invoke(app, ["init", "--yes"])

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_init_force_overwrites_existing_config(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text("allow: false\ntasks: {}\n", encoding="utf-8")
        result = runner.invoke(app, ["init", "--yes", "--force"])
        config = _read_yaml(Path(CONFIG_NAME))

    assert result.exit_code == 0
    assert config["allow"] is True
    assert "sdk" in config["tasks"]


def test_init_with_flags_creates_valid_task(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            app,
            [
                "init",
                "--task",
                "custom-sdk",
                "--input",
                "../openapi.yaml",
                "--language",
                "dart",
                "--template-dir",
                "../templates/dart",
                "--output",
                "../pkg/api",
                "--clean",
                "../pkg/api",
                "--before",
                "echo before",
                "--after",
                "echo after",
            ],
        )
        config = _read_yaml(Path(CONFIG_NAME))

    task = config["tasks"]["custom-sdk"]
    assert result.exit_code == 0
    assert task["input"] == "../openapi.yaml"
    assert task["language"] == "dart"
    assert task["templateDir"] == "../templates/dart"
    assert task["output"] == "../pkg/api"
    assert task["clean"] == ["../pkg/api"]
    assert task["before"] == [{"run": "echo before"}]
    assert task["after"] == [{"run": "echo after"}]


def test_task_add_adds_task_and_preserves_defaults_and_existing_tasks(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text(
            """
allow: true
defaults:
  input: ./openapi.yaml
tasks:
  admin-sdk:
    language: typescript
    templateDir: ./templates/next
    output: ./admin/lib
""".strip(),
            encoding="utf-8",
        )
        result = runner.invoke(
            app,
            [
                "task",
                "add",
                "mobile-api",
                "--language",
                "dart",
                "--template-dir",
                "./templates/dart",
                "--output",
                "./mobile/pkg/api",
                "--clean",
                "./mobile/pkg/api",
                "--yes",
            ],
        )
        config = _read_yaml(Path(CONFIG_NAME))

    assert result.exit_code == 0
    assert config["defaults"] == {"input": "./openapi.yaml"}
    assert "admin-sdk" in config["tasks"]
    assert config["tasks"]["mobile-api"]["language"] == "dart"
    assert config["tasks"]["mobile-api"]["clean"] == ["./mobile/pkg/api"]
    assert "input" not in config["tasks"]["mobile-api"]


def test_task_add_refuses_duplicate_task(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        _write_basic_config(Path(CONFIG_NAME))
        result = runner.invoke(app, ["task", "add", "sdk", "--yes"])

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_task_add_force_replaces_only_that_task(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text(
            """
allow: true
defaults:
  input: ./openapi.yaml
tasks:
  sdk:
    language: typescript
    templateDir: ./templates
    output: ./old
  keep:
    language: dart
    templateDir: ./dart
    output: ./keep
""".strip(),
            encoding="utf-8",
        )
        result = runner.invoke(
            app,
            [
                "task",
                "add",
                "sdk",
                "--force",
                "--language",
                "typescript",
                "--template-dir",
                "./templates",
                "--output",
                "./new",
                "--yes",
            ],
        )
        config = _read_yaml(Path(CONFIG_NAME))

    assert result.exit_code == 0
    assert config["defaults"] == {"input": "./openapi.yaml"}
    assert config["tasks"]["sdk"]["output"] == "./new"
    assert config["tasks"]["keep"]["output"] == "./keep"


def test_task_add_refuses_when_allow_is_not_true(tmp_path: Path) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text(
            """
allow: false
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    output: ./generated
""".strip(),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["task", "add", "other", "--yes"])

    assert result.exit_code == 1
    assert "allow: true" in result.output


def test_generate_output_includes_major_stage_messages(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    _patch_emit(monkeypatch)

    with runner.isolated_filesystem(temp_dir=tmp_path):
        _write_basic_config(Path(CONFIG_NAME))
        result = runner.invoke(app, ["generate"])

    assert result.exit_code == 0
    assert "Loading Codepotg.yaml" in result.output
    assert "Resolving task" in result.output
    assert "Validating task" in result.output
    assert "Loading OpenAPI document" in result.output
    assert "Summary" in result.output


def test_generate_failure_includes_command_output_and_context(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    _patch_emit(monkeypatch)
    command = _python_command(
        "import sys; print('bad output'); print('bad err', file=sys.stderr); sys.exit(3)"
    )

    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path(CONFIG_NAME).write_text(
            yaml.safe_dump(
                {
                    "allow": True,
                    "tasks": {
                        "sdk": {
                            "input": "./openapi.yaml",
                            "language": "typescript",
                            "output": "./generated",
                            "after": [
                                {
                                    "name": "Typecheck generated files",
                                    "run": command,
                                }
                            ],
                        }
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["generate"])

    assert result.exit_code == 1
    assert "Task failed: sdk" in result.output
    assert "Stage: after command" in result.output
    assert "Typecheck generated files" in result.output
    assert "exit code: 3" in result.output
    assert "bad output" in result.output
    assert "bad err" in result.output
    assert "cmd:" in result.output
    assert "sys.exit(3)" in result.output


def _read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_basic_config(path: Path) -> None:
    path.write_text(
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    output: ./generated
""".strip(),
        encoding="utf-8",
    )


def _patch_emit(monkeypatch):
    def fake_emit(request):
        return EmitOutput(
            input_path=request.input_path,
            language=request.language,
            output_path=request.output_path,
            dry_run=request.dry_run,
            planned=[request.output_path / "planned.ts"],
        )

    monkeypatch.setattr(generate_workflow, "run_emit", fake_emit)


def _python_command(code: str) -> str:
    escaped = code.replace('"', r'\"')
    return f'"{sys.executable}" -c "{escaped}"'
