"""Emit summary rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_key_value_table


def render_emit_summary(result) -> None:
    """Render the emit summary table."""
    render_key_value_table(
        "Emit Summary",
        {
            "Input": getattr(result, "input_path", "-"),
            "Language": getattr(result, "language", "-"),
            "Output": getattr(result, "output_path", "-"),
            "Dry Run": getattr(result, "dry_run", False),
            "Planned": len(getattr(result, "planned", [])),
            "Written": len(getattr(result, "written", [])),
            "Updated": len(getattr(result, "updated", [])),
            "Unchanged": len(getattr(result, "unchanged", [])),
            "Skipped": len(getattr(result, "skipped", [])),
        },
        highlight_zero=True,
    )
