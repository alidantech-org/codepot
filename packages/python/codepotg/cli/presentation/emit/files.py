"""Emit file table rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_rows_table


def render_emit_files(title: str, files) -> None:
    """Render emitted file paths."""
    if not files:
        return

    rows = [(str(path),) for path in files]

    render_rows_table(
        title,
        ["Path"],
        rows,
    )
