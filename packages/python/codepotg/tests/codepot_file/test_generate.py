from __future__ import annotations

from pathlib import Path

import pytest

from app.models import EmitOutput
from app.models.inputs import GenerateInput
from app.workflows import generate as generate_workflow
from core.errors import CommandError, ConfigError


def test_allow_false_refuses_generation(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        """
allow: false
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
""",
    )

    with pytest.raises(ConfigError, match="allow: true"):
        generate_workflow.run_generate(GenerateInput(config_path=config))


def test_one_task_without_name_runs_task(tmp_path: Path, monkeypatch) -> None:
    config = _write_basic_config(tmp_path, "sdk")
    calls = _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(GenerateInput(config_path=config))

    assert [task.name for task in result.tasks] == ["sdk"]
    assert calls[0].language == "typescript"


def test_multiple_tasks_without_name_fails_with_available_names(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  admin:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
  mobile:
    input: ./openapi.yaml
    language: dart
    templateDir: ./templates
    output: ./pkg/api
""",
    )

    with pytest.raises(ConfigError, match="Available tasks"):
        generate_workflow.run_generate(GenerateInput(config_path=config))


def test_named_task_runs_selected_task(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  admin:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
  mobile:
    input: ./openapi.yaml
    language: dart
    templateDir: ./templates
    output: ./pkg/api
""",
    )
    calls = _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(GenerateInput(config_path=config, task_name="mobile"))

    assert [task.name for task in result.tasks] == ["mobile"]
    assert calls[0].language == "dart"


def test_all_tasks_runs_tasks_in_file_order(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  admin:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
  mobile:
    input: ./openapi.yaml
    language: dart
    templateDir: ./templates
    output: ./pkg/api
""",
    )
    calls = _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(GenerateInput(config_path=config, all_tasks=True))

    assert [task.name for task in result.tasks] == ["admin", "mobile"]
    assert [call.language for call in calls] == ["typescript", "dart"]


def test_dry_run_does_not_execute_commands_and_calls_emit_dry_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
    before:
      - run: python -c "raise SystemExit(9)"
    after:
      - run: python -c "raise SystemExit(9)"
""",
    )
    calls = _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(GenerateInput(config_path=config, dry_run=True))

    assert calls[0].dry_run is True
    assert any("Would run" in diagnostic.message for diagnostic in result.diagnostics)


def test_refresh_deletes_clean_path_only_when_requested(tmp_path: Path, monkeypatch) -> None:
    clean_dir = tmp_path / "lib" / "gen"
    clean_dir.mkdir(parents=True)
    (clean_dir / "file.txt").write_text("x", encoding="utf-8")
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
    clean:
      - ./lib/gen
""",
    )
    _patch_emit(monkeypatch)

    generate_workflow.run_generate(GenerateInput(config_path=config))
    assert clean_dir.exists()

    generate_workflow.run_generate(GenerateInput(config_path=config, refresh=True))
    assert not clean_dir.exists()


def test_optional_command_failure_warns_and_continues(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
    before:
      - run: python -c "raise SystemExit(7)"
        optional: true
""",
    )
    _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(GenerateInput(config_path=config))

    assert any("Optional command failed" in diagnostic.message for diagnostic in result.diagnostics)


def test_required_command_failure_fails_task(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
    before:
      - run: python -c "raise SystemExit(7)"
""",
    )
    _patch_emit(monkeypatch)

    with pytest.raises(CommandError):
        generate_workflow.run_generate(GenerateInput(config_path=config))


def test_generate_merges_defaults_into_task(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
defaults:
  input: ./openapi.yaml
tasks:
  sdk:
    language: typescript
    templateDir: ./templates
    output: ./lib
""",
    )
    calls = _patch_emit(monkeypatch)

    generate_workflow.run_generate(GenerateInput(config_path=config))

    assert calls[0].input_path == (tmp_path / "openapi.yaml").resolve()


def test_task_can_share_defaults_before_and_after(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path,
        """
allow: true
defaults:
  input: ./openapi.yaml
  language: typescript
  templateDir: ./templates
  output: ./lib
  before:
    - run: echo before
  after:
    - run: echo after
tasks:
  admin:
    output: ./admin
  mobile:
    output: ./mobile
""",
    )
    calls = _patch_emit(monkeypatch)

    result = generate_workflow.run_generate(
        GenerateInput(config_path=config, all_tasks=True, dry_run=True)
    )

    assert [call.input_path for call in calls] == [
        (tmp_path / "openapi.yaml").resolve(),
        (tmp_path / "openapi.yaml").resolve(),
    ]
    assert sum("Would run" in diagnostic.message for diagnostic in result.diagnostics) == 4


def _patch_emit(monkeypatch):
    calls = []

    def fake_emit(request):
        calls.append(request)
        return EmitOutput(
            input_path=request.input_path,
            language=request.language,
            output_path=request.output_path,
            dry_run=request.dry_run,
            planned=[request.output_path / "planned.ts"],
        )

    monkeypatch.setattr(generate_workflow, "run_emit", fake_emit)
    return calls


def _write_basic_config(tmp_path: Path, task_name: str) -> Path:
    return _write_config(
        tmp_path,
        f"""
allow: true
tasks:
  {task_name}:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates
    output: ./lib
""",
    )


def _write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "CodepotFile.yml"
    path.write_text(content.strip(), encoding="utf-8")
    return path
