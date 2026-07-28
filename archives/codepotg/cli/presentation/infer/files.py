"""Inference file rendering."""

from __future__ import annotations

from archives.codepotg.cli.presentation.core.tables import render_rows_table


def render_infer_written_files(files) -> None:
    """Render inference output files."""
    if not files:
        return

    rows = [(str(path),) for path in files]

    render_rows_table(
        "Written Files",
        ["Path"],
        rows,
    )
