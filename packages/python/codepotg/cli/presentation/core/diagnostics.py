"""Reusable diagnostics rendering helpers."""

from __future__ import annotations

from collections import Counter

from cli.presentation.core.tables import render_rows_table


def render_diagnostics(diagnostics, *, title: str = "Diagnostics") -> None:
    """Render diagnostic objects with level/message fields."""
    if not diagnostics:
        return

    rows = [
        (
            _style_level(getattr(item, "level", "-")),
            getattr(item, "message", "-"),
        )
        for item in diagnostics
    ]

    render_rows_table(
        title,
        ["Level", "Message"],
        rows,
    )


def count_diagnostics(diagnostics) -> Counter[str]:
    """Count diagnostics by level for callers that explicitly want summaries."""
    return Counter(str(getattr(item, "level", "-")).lower() for item in diagnostics)


def _style_level(level: str) -> str:
    normalized = str(level).lower()

    if normalized == "error":
        return "[bold red]x error[/bold red]"

    if normalized == "warning":
        return "[bold yellow]! warning[/bold yellow]"

    if normalized == "info":
        return "[bold cyan]i info[/bold cyan]"

    return f"[dim]{level}[/dim]"
