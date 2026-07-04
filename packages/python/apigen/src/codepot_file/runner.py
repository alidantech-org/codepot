"""CodepotFile command execution and refresh cleanup."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from codepot_file.models import CodepotCommand, CodepotTask
from core.errors import CommandError, ConfigError


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
) -> RunnerResult:
    """Run user-defined commands in order."""
    result = RunnerResult()

    for command in commands:
        cwd = (command.cwd or config_root).resolve()
        env = os.environ.copy()
        env.update(task.env)
        env.update(command.env)

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
            result.diagnostics.append(f"Would run: {command.run} (cwd: {cwd})")
            continue

        try:
            completed = subprocess.run(
                command.run,
                cwd=str(cwd),
                env=env,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            message = f"Command could not start: {command.run}\nWorking directory: {cwd}"
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

        if verbose and completed.stdout:
            result.diagnostics.append(completed.stdout.rstrip())
        if verbose and completed.stderr:
            result.diagnostics.append(completed.stderr.rstrip())

        if completed.returncode == 0:
            continue

        message = (
            f"Command failed ({completed.returncode}): {command.run}"
            f"\nWorking directory: {cwd}"
        )
        if command.optional:
            result.diagnostics.append(f"Optional command failed; continuing. {message}")
            continue

        raise CommandError(message)

    return result


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
