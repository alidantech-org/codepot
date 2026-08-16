from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dryv_cli.app.context import AppContext
from dryv_cli.connections.author import AuthorClient
from dryv_cli.presentation import render_diagnostics
from dryv_cli.project import ProjectError, discover_project
from dryv_cli.resolvers import resolve_author


def compile_command(context: AppContext, args: argparse.Namespace) -> int:
    project = discover_project(context.start)
    target = resolve_author(project, args.author)
    if target is None:
        raise ProjectError("CLI_AUTHOR_MISSING", "compile requires source.author or --author")
    result = AuthorClient().compile(
        target.target,
        project_root=project.root,
        representation=args.format,
    )
    render_diagnostics(context.console, result.diagnostics)
    if not result.ok or result.content is None:
        return 1
    if args.output:
        path = _output_path(project.root, args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result.content)
        context.console.write(f"Wrote Canonical IR: {path.relative_to(project.root).as_posix()}")
    else:
        sys.stdout.buffer.write(result.content)
        if result.content and not result.content.endswith(b"\n"):
            sys.stdout.buffer.write(b"\n")
    return 0


def _output_path(root: Path, value: str) -> Path:
    if not value or Path(value).is_absolute():
        raise ProjectError("CLI_COMPILE_OUTPUT", "compile output must be project-relative")
    target = (root / value).resolve(strict=False)
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ProjectError("CLI_COMPILE_OUTPUT", "compile output escapes the project root") from exc
    return target


__all__ = ["compile_command"]
