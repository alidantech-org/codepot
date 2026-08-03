"""Validate command presentation."""

from __future__ import annotations

from archives.codepot.src.cli.presentation.console import console
from archives.codepot.src.contracts.spec.context import SpecContext


def print_validate_result(context: SpecContext) -> None:
    """Print spec validation result."""

    metadata = context.metadata
    counts = context.counts

    console.print("[green]OK[/green] Spec validated.")
    console.print(f"Project: [bold]{metadata.project.project_key}[/bold]")
    console.print(f"Version: {metadata.project.version}")
    console.print(f"Records: {counts.records_total}")
    console.print(f"Resources: {counts.resources}")
    console.print(f"Models: {counts.models}")
    console.print(f"DTOs: {counts.dtos}")
