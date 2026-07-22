"""Inference schema table rendering."""

from __future__ import annotations

from cli.presentation.core.console import console
from cli.presentation.core.tables import render_rows_table


def render_unknown_schemas(schemas) -> None:
    """Render unknown schemas."""
    if not schemas:
        return

    console.print("[bold yellow]⚠ Unknown schemas detected[/bold yellow]")

    rows = [
        (
            getattr(schema, "name", "-"),
            getattr(schema, "ref", "-"),
            getattr(schema, "x_codegen_kind", "-"),
            ", ".join(getattr(schema, "keys", [])),
        )
        for schema in schemas
    ]

    render_rows_table(
        "Unknown Schemas",
        ["Name", "Ref", "x-codegen.kind", "Keys"],
        rows,
    )


def render_alias_schemas(schemas) -> None:
    """Render alias schemas."""
    if not schemas:
        return

    rows = [
        (
            getattr(schema, "name", "-"),
            getattr(schema, "kind", "-"),
            getattr(schema, "alias_of", "-"),
            getattr(schema, "resource", "-"),
        )
        for schema in schemas
    ]

    render_rows_table(
        "Alias Schemas",
        ["Name", "Kind", "Alias Of", "Resource"],
        rows,
    )
