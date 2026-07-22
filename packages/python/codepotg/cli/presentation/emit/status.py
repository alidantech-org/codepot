"""Emit status rendering."""

from __future__ import annotations

from cli.presentation.core.console import console


def render_emit_status(result) -> None:
    """Render emit status."""
    language = getattr(result, "language", "-")
    output_path = getattr(result, "output_path", "-")
    dry_run = bool(getattr(result, "dry_run", False))

    if dry_run:
        console.print(
            f"[bold cyan]i Emit planned[/bold cyan] [dim]{language} -> {output_path}[/dim]"
        )
        return

    console.print(
        f"[bold green]+ Emit completed[/bold green] [dim]{language} -> {output_path}[/dim]"
    )
