"""Presentation helpers for emit results."""

from __future__ import annotations

from cli.presentation.emit.diagnostics import render_diagnostics
from cli.presentation.emit.files import render_emit_files
from cli.presentation.emit.status import render_emit_status
from cli.presentation.emit.summary import render_emit_summary


def render_emit_result(result, *, verbose: bool = False) -> None:
    """Render an EmitOutput-like object."""
    render_emit_status(result)
    render_emit_summary(result)

    if not verbose:
        return

    dry_run = bool(getattr(result, "dry_run", False))

    render_emit_files("Planned Files", getattr(result, "planned", []))

    if not dry_run:
        render_emit_files("Written Files", getattr(result, "written", []))
        render_emit_files("Updated Files", getattr(result, "updated", []))
        render_emit_files("Unchanged Files", getattr(result, "unchanged", []))
        render_emit_files("Skipped Files", getattr(result, "skipped", []))

    render_diagnostics(getattr(result, "diagnostics", []))
