from __future__ import annotations

import sys
from pathlib import Path

import pytest

from codepot_file.models import CodepotCommand, CodepotTask
from codepot_file.runner import run_commands
from core.errors import CommandError


def test_verbose_command_runner_streams_stdout_and_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = _python_command(
        "import sys; print('hello stdout'); print('hello stderr', file=sys.stderr)"
    )

    run_commands(
        (CodepotCommand(name="Talk", run=command),),
        task=_task(tmp_path),
        config_root=tmp_path,
        verbose=True,
    )

    captured = capsys.readouterr()
    assert "hello stdout" in captured.out
    assert "hello stderr" in captured.err


def test_non_verbose_required_failure_includes_captured_output(tmp_path: Path) -> None:
    command = _python_command(
        "import sys; print('bad output'); print('bad err', file=sys.stderr); sys.exit(3)"
    )

    with pytest.raises(CommandError) as exc_info:
        run_commands(
            (CodepotCommand(name="Failing command", run=command),),
            task=_task(tmp_path),
            config_root=tmp_path,
            verbose=False,
        )

    message = str(exc_info.value)
    assert "Failing command" in message
    assert "exit code: 3" in message
    assert "bad output" in message
    assert "bad err" in message
    assert command in message
    assert str(tmp_path.resolve()) in message


def test_optional_failure_warns_and_hides_output_without_verbose(tmp_path: Path) -> None:
    command = _python_command(
        "import sys; print('optional output'); print('optional err', file=sys.stderr); sys.exit(3)"
    )

    result = run_commands(
        (CodepotCommand(name="Optional", run=command, optional=True),),
        task=_task(tmp_path),
        config_root=tmp_path,
        verbose=False,
    )

    warning = "\n".join(result.diagnostics)
    assert "Optional command failed" in warning
    assert "exit code: 3" in warning
    assert "Output:" not in warning


def test_optional_failure_includes_output_with_verbose(tmp_path: Path) -> None:
    command = _python_command(
        "import sys; print('optional output'); print('optional err', file=sys.stderr); sys.exit(3)"
    )

    result = run_commands(
        (CodepotCommand(name="Optional", run=command, optional=True),),
        task=_task(tmp_path),
        config_root=tmp_path,
        verbose=True,
    )

    warning = "\n".join(result.diagnostics)
    assert "Optional command failed" in warning
    assert "optional output" in warning
    assert "optional err" in warning


def test_dry_run_does_not_run_commands(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    command = _python_command(f"from pathlib import Path; Path(r'{marker}').write_text('ran')")

    result = run_commands(
        (CodepotCommand(name="Dry", run=command),),
        task=_task(tmp_path),
        config_root=tmp_path,
        dry_run=True,
    )

    assert not marker.exists()
    assert result.commands[0].skipped is True
    assert "Would run" in result.diagnostics[0]


def _task(tmp_path: Path) -> CodepotTask:
    return CodepotTask(
        name="sdk",
        input=tmp_path / "openapi.yaml",
        language="debug",
        output=tmp_path / "out",
        template_dir=tmp_path / "templates",
    )


def _python_command(code: str) -> str:
    escaped = code.replace('"', r"\"")
    return f'"{sys.executable}" -c "{escaped}"'
