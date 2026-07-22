"""Inspect resource rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_rows_table


def render_inspect_resources(resources) -> None:
    """Render detected OpenAPI resources."""
    if not resources:
        return

    rows = [
        (
            getattr(resource, "name", "-"),
            getattr(resource, "path", "-"),
            getattr(resource, "operations_count", 0),
        )
        for resource in resources
    ]

    render_rows_table(
        "Detected Resources",
        ["Resource", "Path", "Operations"],
        rows,
    )
