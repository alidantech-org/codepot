"""Inspect summary rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_key_value_table


def render_inspect_summary(result) -> None:
    """Render OpenAPI inspection summary."""
    render_key_value_table(
        "OpenAPI Summary",
        {
            "Title": getattr(result, "title", "-"),
            "OpenAPI": getattr(result, "openapi_version", "-"),
            "API Version": getattr(result, "api_version", "-"),
            "Paths": getattr(result, "paths_count", 0),
            "Operations": getattr(result, "operations_count", 0),
            "Schemas": getattr(result, "schemas_count", 0),
            "Responses": getattr(result, "responses_count", 0),
            "Request Bodies": getattr(result, "request_bodies_count", 0),
            "Parameters": getattr(result, "parameters_count", 0),
            "Refs": getattr(result, "refs_count", 0),
            "Component Refs": getattr(result, "component_refs_count", 0),
            "Missing Component Refs": getattr(result, "missing_component_refs_count", 0),
        },
        highlight_zero=True,
    )
