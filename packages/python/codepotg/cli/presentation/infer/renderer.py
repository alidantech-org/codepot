"""CLI presentation for infer results."""

from __future__ import annotations

from cli.presentation.infer.diagnostics import render_diagnostics
from cli.presentation.infer.files import render_infer_written_files
from cli.presentation.infer.schemas import render_alias_schemas, render_unknown_schemas
from cli.presentation.infer.status import render_infer_status
from cli.presentation.infer.summary import render_infer_summary


def render_infer_result(result, *, verbose: bool = False) -> None:
    """Render an InferOutput-like object."""
    render_infer_status(result)
    render_infer_summary(result)
    render_infer_written_files(getattr(result, "written", []))

    if verbose:
        render_unknown_schemas(getattr(result, "unknown_schemas", []))
        render_alias_schemas(getattr(result, "alias_schemas", []))
        render_diagnostics(getattr(result, "diagnostics", []))
