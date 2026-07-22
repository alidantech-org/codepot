"""Table builders."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from rich.table import Table


def make_key_value_table(title: str, rows: Mapping[str, Any] | Iterable[tuple[str, Any]]) -> Table:
    table = Table(title=title, box=None, show_header=False)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    items = rows.items() if isinstance(rows, Mapping) else rows
    for key, value in items:
        table.add_row(str(key), str(value))
    return table


def make_file_table(title: str, files: Iterable[Any]) -> Table:
    table = Table(title=title)
    table.add_column("Path", style="cyan")
    table.add_column("Template")
    table.add_column("Source")
    for file in files:
        table.add_row(str(file.path), str(file.template), f"{file.group}: {file.source}")
    return table


def make_issue_table(title: str, issues: Iterable[Any]) -> Table:
    table = Table(title=title)
    table.add_column("Severity")
    table.add_column("Message")
    table.add_column("Path")
    for issue in issues:
        table.add_row(str(issue.severity), str(issue.message), str(issue.path or ""))
    return table


def path_text(path: Path) -> str:
    return path.as_posix()
