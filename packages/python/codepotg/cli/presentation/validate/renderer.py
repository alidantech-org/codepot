"""CLI presentation for validate results."""

from __future__ import annotations

from cli.presentation.validate.diagnostics import render_diagnostics
from cli.presentation.validate.issues import (
    render_validation_errors,
    render_validation_warnings,
)
from cli.presentation.validate.summary import render_validate_summary


def render_validate_result(result, *, verbose: bool = False) -> None:
    """Render a ValidateOutput-like object."""
    render_validate_summary(result)

    render_validation_errors(getattr(result, "errors", []))
    render_validation_warnings(getattr(result, "warnings", []))

    if verbose:
        render_diagnostics(getattr(result, "diagnostics", []))
