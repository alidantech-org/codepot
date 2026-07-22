"""Validation issue rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_rows_table


def render_validation_errors(errors) -> None:
    """Render validation errors."""
    if not errors:
        return

    render_rows_table(
        "Errors",
        ["Message"],
        [(str(message),) for message in errors],
    )


def render_validation_warnings(warnings) -> None:
    """Render validation warnings."""
    if not warnings:
        return

    render_rows_table(
        "Warnings",
        ["Message"],
        [(str(message),) for message in warnings],
    )
