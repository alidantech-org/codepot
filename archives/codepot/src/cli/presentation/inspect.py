"""Inspect command presentation."""

from __future__ import annotations

from rich.table import Table

from archives.codepot.src.cli.presentation.console import console
from archives.codepot.src.contracts.spec.context import SpecContext


def print_inspect_result(context: SpecContext, mode: str) -> None:
    """Print spec inspection result."""

    if mode == "counts":
        _print_counts(context)
        return

    _print_overview(context)


def _print_overview(context: SpecContext) -> None:
    """Print overview inspection."""

    metadata = context.metadata

    console.print(f"[bold]{metadata.project.title}[/bold]")
    console.print(f"Project: {metadata.project.project_key}")
    console.print(f"Version: {metadata.project.version}")
    console.print(f"Spec hash: {metadata.file.hash}")
    _print_counts(context)


def _print_counts(context: SpecContext) -> None:
    """Print counts table."""

    counts = context.counts
    table = Table(title="Spec counts")
    table.add_column("Subject")
    table.add_column("Count", justify="right")

    rows = (
        ("content_types", counts.content_types),
        ("primitives", counts.primitives),
        ("enums", counts.enums),
        ("composites", counts.composites),
        ("entities", counts.entities),
        ("models", counts.models),
        ("dtos", counts.dtos),
        ("resources", counts.resources),
        ("operations", counts.operations),
        ("routes", counts.routes),
        ("records_total", counts.records_total),
    )

    for name, value in rows:
        table.add_row(name, str(value))

    console.print(table)
