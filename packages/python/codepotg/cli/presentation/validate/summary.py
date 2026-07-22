"""Validation summary rendering."""

from __future__ import annotations

from cli.presentation.core.console import console


def render_validate_summary(result) -> None:
    """Render validation status."""
    valid = bool(getattr(result, "valid", False))
    input_path = getattr(result, "input_path", "-")

    if valid:
        console.print(f"[bold green]✓ Validation passed[/bold green] [dim]{input_path}[/dim]")
        return

    console.print(f"[bold red]✗ Validation failed[/bold red] [dim]{input_path}[/dim]")
