"""Template command presentation."""

from __future__ import annotations

from archives.codepot.src.cli.presentation.console import console
from archives.codepot.src.pipeline.templates.validator import TemplateValidationResult


def print_template_validation_result(result: TemplateValidationResult) -> None:
    """Print template validation result."""

    if result.is_valid:
        console.print("[green]OK[/green] Template package is valid.")
    else:
        console.print("[red]X[/red] Template package is invalid.")

    for error in result.errors:
        prefix = f"{error.template_id}: " if error.template_id else ""
        console.print(f"[red]error:[/red] {prefix}{error.message}")

    for warning in result.warnings:
        prefix = f"{warning.template_id}: " if warning.template_id else ""
        console.print(f"[yellow]warning:[/yellow] {prefix}{warning.message}")
