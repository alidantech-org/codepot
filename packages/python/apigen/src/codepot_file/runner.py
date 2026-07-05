"""CodepotFile command execution and refresh cleanup."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from app.models.events import RuntimeEvent
from codepot_file.models import CodepotCommand, CodepotTask
from core.errors import CommandError, ConfigError

ProgressSink = Callable[[RuntimeEvent], None]


@dataclass(frozen=True)
class CommandResult:
    """Result of a user-defined command."""

    name: str | None
    run: str
    cwd: Path
    returncode: int = 0
    optional: bool = False
    skipped: bool = False
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class RunnerResult:
    """Accumulated command and cleanup result."""

    commands: list[CommandResult] = field(default_factory=list)
    cleaned: list[Path] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)


def clean_task_paths(
    task: CodepotTask,
    *,
    config_root: Path,
    dry_run: bool = False,
) -> RunnerResult:
    """Delete configured clean paths with safety checks."""
    result = RunnerResult()

    for path in task.clean:
        clean_path = path.resolve()
        _validate_clean_path(clean_path, config_root=config_root, output_path=task.output)
        result.diagnostics.append(f"{'Would delete' if dry_run else 'Deleting'}: {clean_path}")

        if not dry_run and clean_path.exists():
            if clean_path.is_dir():
                shutil.rmtree(clean_path)
            else:
                clean_path.unlink()

        result.cleaned.append(clean_path)

    return result


def run_commands(
    commands: tuple[CodepotCommand, ...],
    *,
    task: CodepotTask,
    config_root: Path,
    dry_run: bool = False,
    verbose: bool = False,
    phase: str = "command",
    progress: ProgressSink | None = None,
) -> RunnerResult:
    """Run user-defined commands in order."""
    result = RunnerResult()

    for command in commands:
        cwd = (command.cwd or config_root).resolve()
        env = os.environ.copy()
        env.update(task.env)
        env.update(command.env)
        command_label = command.name or command.run

        if dry_run:
            result.commands.append(
                CommandResult(
                    name=command.name,
                    run=command.run,
                    cwd=cwd,
                    optional=command.optional,
                    skipped=True,
                )
            )
            message = f"Would run {phase} command: {command_label}"
            result.diagnostics.append(f"{message}\n  cwd: {cwd}\n  cmd: {command.run}")
            _notify(
                progress,
                "command_dry_run",
                message,
                level="info",
                details={"cwd": str(cwd), "cmd": command.run, "phase": phase},
            )
            continue

        _notify(
            progress,
            "command_start",
            f"Running {phase} command: {command_label}",
            details={"cwd": str(cwd), "cmd": command.run, "phase": phase},
        )

        try:
            completed = _run_command(
                command.run,
                cwd=str(cwd),
                env=env,
                verbose=verbose,
                progress=progress,
            )
        except OSError as exc:
            message = _format_command_failure(
                title="Command could not start",
                command=command,
                cwd=cwd,
                returncode=None,
                stdout="",
                stderr=str(exc),
            )
            if command.optional:
                result.diagnostics.append(f"Optional command failed; continuing. {message}")
                continue
            raise CommandError(message) from exc

        command_result = CommandResult(
            name=command.name,
            run=command.run,
            cwd=cwd,
            returncode=completed.returncode,
            optional=command.optional,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        result.commands.append(command_result)

        if completed.returncode == 0:
            _notify(
                progress,
                "command_success",
                f"Completed {phase} command: {command_label}",
                details={"cwd": str(cwd), "cmd": command.run, "phase": phase},
            )
            continue

        message = _format_command_failure(
            title="Command failed",
            command=command,
            cwd=cwd,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if command.optional:
            if verbose:
                result.diagnostics.append(f"Optional command failed; continuing.\n{message}")
            else:
                result.diagnostics.append(
                    "Optional command failed; continuing.\n"
                    f"  command: {command_label}\n"
                    f"  exit code: {completed.returncode}\n"
                    f"  cwd: {cwd}\n"
                    f"  cmd: {command.run}"
                )
            _notify(
                progress,
                "command_warning",
                f"Optional command failed: {command_label}",
                level="warning",
                details={
                    "cwd": str(cwd),
                    "cmd": command.run,
                    "phase": phase,
                    "returncode": completed.returncode,
                },
            )
            continue

        _notify(
            progress,
            "command_error",
            f"Command failed with exit code {completed.returncode}: {command_label}",
            level="error",
            details={
                "cwd": str(cwd),
                "cmd": command.run,
                "phase": phase,
                "returncode": completed.returncode,
            },
        )
        raise CommandError(message)

    return result


@dataclass(frozen=True)
class _CompletedCommand:
    returncode: int
    stdout: str
    stderr: str


def _run_command(
    command: str,
    *,
    cwd: str,
    env: dict[str, str],
    verbose: bool,
    progress: ProgressSink | None,
) -> _CompletedCommand:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    def read_stream(stream, lines: list[str], stage: str, target) -> None:
        try:
            for line in iter(stream.readline, ""):
                lines.append(line)
                if verbose:
                    target.write(line)
                    target.flush()
                    _notify(
                        progress,
                        stage,
                        line.rstrip("\n"),
                        details={"stream": stage},
                    )
        finally:
            stream.close()

    stdout_thread = threading.Thread(
        target=read_stream,
        args=(process.stdout, stdout_lines, "command_stdout", sys.stdout),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=read_stream,
        args=(process.stderr, stderr_lines, "command_stderr", sys.stderr),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()
    returncode = process.wait()
    stdout_thread.join()
    stderr_thread.join()

    return _CompletedCommand(
        returncode=returncode,
        stdout="".join(stdout_lines),
        stderr="".join(stderr_lines),
    )


def _format_command_failure(
    *,
    title: str,
    command: CodepotCommand,
    cwd: Path,
    returncode: int | None,
    stdout: str,
    stderr: str,
) -> str:
    label = command.name or command.run
    lines = [f"{title}: {label}"]
    if returncode is not None:
        lines.append(f"  exit code: {returncode}")
    lines.extend(
        [
            f"  cwd: {cwd}",
            f"  cmd: {command.run}",
        ]
    )
    output = _combined_output(stdout, stderr)
    if output:
        lines.extend(["", "Output:", output.rstrip()])
    return "\n".join(lines)


def _combined_output(stdout: str, stderr: str) -> str:
    parts = []
    if stdout:
        parts.append(stdout)
    if stderr:
        parts.append(stderr)
    return "\n".join(part.rstrip("\n") for part in parts if part)


def _notify(
    progress: ProgressSink | None,
    stage: str,
    message: str,
    *,
    level: str = "info",
    details: dict[str, object] | None = None,
) -> None:
    if progress is None:
        return
    progress(RuntimeEvent(stage=stage, message=message, level=level, details=details or {}))


def _validate_clean_path(
    clean_path: Path,
    *,
    config_root: Path,
    output_path: Path,
) -> None:
    root = config_root.resolve()
    output = output_path.resolve()
    home = Path.home().resolve()

    if clean_path == home:
        raise ConfigError(f"Refusing to clean user home: {clean_path}")

    anchor_path = Path(clean_path.anchor).resolve()
    if clean_path == anchor_path:
        raise ConfigError(f"Refusing to clean filesystem root: {clean_path}")

    if not _is_relative_to(clean_path, root) and not _is_relative_to(clean_path, output):
        raise ConfigError(
            f"Refusing to clean path outside config directory or task output: {clean_path}"
        )


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
