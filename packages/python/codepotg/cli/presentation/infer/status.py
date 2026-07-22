"""Inference status rendering."""

from __future__ import annotations

from cli.presentation.core.console import console


def render_infer_status(result) -> None:
    """Render inference status."""
    input_path = getattr(result, "input_path", "-")
    console.print(f"[bold green]✓ Inference completed[/bold green] [dim]{input_path}[/dim]")
