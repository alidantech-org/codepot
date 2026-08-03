"""Emit file table rendering."""

from __future__ import annotations

from archives.codepotg.cli.presentation.core.tables import render_rows_table


def render_emit_files(title: str, files) -> None:
    """Render emitted file paths with normalized separators."""
    if not files:
        return

    rows = [(_display_path(path),) for path in files]

    render_rows_table(
        title,
        ["Path"],
        rows,
    )


def _display_path(path: object) -> str:
    return str(path).replace("\\", "/")
