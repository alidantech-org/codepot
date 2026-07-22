"""Reusable Rich table helpers for CLI presentation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any

from rich import box
from rich.table import Table
from rich.text import Text

from cli.constants.defaults import ACRONYM_REPLACEMENTS, NUMERIC_COLUMN_TOKENS
from cli.presentation.core.console import console


def render_key_value_table(
    title: str,
    data: Mapping[str, Any] | object,
    *,
    key_column: str = "Metric",
    value_column: str = "Value",
    highlight_zero: bool = False,
) -> None:
    """Render mapping or dataclass-like object as a styled key/value table."""
    values = _to_mapping(data)

    table = create_table(title)
    table.add_column(key_column, style="bold #378ADD", no_wrap=True)
    table.add_column(value_column, style="white", justify="right")

    for key, value in values.items():
        table.add_row(_format_key(key), _format_value(value, highlight_zero=highlight_zero))

    console.print(table)


def render_rows_table(
    title: str,
    columns: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    empty_message: str = "No rows.",
) -> None:
    """Render row data as a styled Rich table."""
    if not rows:
        console.print(f"[dim]{empty_message}[/dim]")
        return

    table = create_table(title)

    for index, column in enumerate(columns):
        is_numeric = index > 0 and _looks_numeric_column(column)
        justify = "right" if is_numeric else "left"

        if index == 0:
            style = "bold #378ADD"  # key column: blue accent
        elif is_numeric:
            style = "bold white"  # numeric columns: prominent
        else:
            style = "dim"  # secondary text columns: recede

        table.add_column(column, style=style, justify=justify, no_wrap=index == 0)

    for row in rows:
        table.add_row(*[_format_value(value) for value in row])

    console.print(table)


def create_table(title: str) -> Table:
    """Create the default CLI table style."""
    return Table(
        title=Text(title, style="bold #7F77DD"),
        box=box.HEAVY,
        show_header=True,
        header_style="dim",
        border_style="bright_black",
        row_styles=["none", "on grey3"],
        title_justify="left",
        expand=False,
        padding=(0, 2),
    )


def _to_mapping(data: Mapping[str, Any] | object) -> Mapping[str, Any]:
    if isinstance(data, Mapping):
        return data

    if is_dataclass(data):
        return asdict(data)

    if hasattr(data, "__dict__"):
        return vars(data)

    return {"value": data}


def _format_key(key: str) -> str:
    """Format table keys while preserving common acronyms."""
    text = str(key).replace("_", " ").title()

    for source, target in ACRONYM_REPLACEMENTS.items():
        text = text.replace(source, target)

    return text


def _format_value(value: Any, *, highlight_zero: bool = False) -> str:
    if value is None:
        return "[dim]-[/dim]"

    if isinstance(value, bool):
        return "[bold green]yes[/bold green]" if value else "[dim]no[/dim]"

    if isinstance(value, int | float):
        if value == 0 and highlight_zero:
            return "[dim]0[/dim]"
        formatted = f"{value:,}" if isinstance(value, int) else f"{value:,.2f}"
        return f"[bold]{formatted}[/bold]"

    if isinstance(value, list | tuple | set):
        count = len(value)
        return f"[bold]{count:,}[/bold]" if count else "[dim]0[/dim]"

    if isinstance(value, dict):
        count = len(value)
        return f"[bold]{count:,}[/bold]" if count else "[dim]0[/dim]"

    text = str(value)
    if text in {"-", ""}:
        return "[dim]-[/dim]"

    return text


def _looks_numeric_column(column: str) -> bool:
    lowered = column.lower()
    return any(token in lowered for token in NUMERIC_COLUMN_TOKENS)
