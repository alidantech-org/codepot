"""Inspect status rendering."""

from __future__ import annotations

from cli.presentation.core.console import console


def render_inspect_status(result) -> None:
    """Render inspection status."""
    input_path = getattr(result, "input_path", "-")
    console.print(f"[bold green]✓ Inspection completed[/bold green] [dim]{input_path}[/dim]")
