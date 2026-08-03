"""Emit command renderer."""

from __future__ import annotations

from collections import Counter

from archives.codepot.src.app import EmitResult
from archives.codepot.src.cli.presentation.console import console


def render_emit_result(result: EmitResult) -> None:
    mode = "Dry run" if result.dry_run else "Emitting"
    console.print(
        f"[bold]{mode} {result.language} -> {result.output_path.as_posix()}[/bold]",
    )
    console.print()

    for file in result.files:
        template_id = file.template_id or ""
        console.print(f"  {file.status:<9} {file.path.as_posix():32} {template_id}")

    counts = Counter(file.status for file in result.files)
    console.print()
    if result.dry_run:
        console.print(f"{len(result.files)} files processed")
    else:
        console.print(
            f"{len(result.files)} files processed - "
            f"{counts['created']} created - "
            f"{counts['updated']} updated - "
            f"{counts['unchanged']} unchanged",
        )

    if result.format and result.formatter_command:
        console.print()
        console.print("[bold]Formatter[/bold]")
        console.print(f"Would run: {result.formatter_command}")

    if result.run_hooks and result.hook_commands:
        console.print()
        console.print("[bold]Hooks[/bold]")
        for command in result.hook_commands:
            console.print(f"Would run: {command}")
