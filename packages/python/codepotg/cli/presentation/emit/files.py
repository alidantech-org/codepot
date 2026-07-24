"""Emit file table rendering."""

from __future__ import annotations

from os import PathLike

from cli.presentation.core.tables import render_rows_table


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
    if isinstance(path, PathLike):
        return path.__fspath__().replace("\\", "/")
    return str(path).replace("\\", "/")
