"""CLI presentation for inspect results."""

from __future__ import annotations

from cli.presentation.inspect.diagnostics import render_diagnostics
from cli.presentation.inspect.resources import render_inspect_resources
from cli.presentation.inspect.status import render_inspect_status
from cli.presentation.inspect.summary import render_inspect_summary


def render_inspect_result(result, *, verbose: bool = False) -> None:
    """Render an InspectOutput-like object."""
    render_inspect_status(result)
    render_inspect_summary(result)
    render_inspect_resources(getattr(result, "resources", []))

    if verbose:
        render_diagnostics(getattr(result, "diagnostics", []))
