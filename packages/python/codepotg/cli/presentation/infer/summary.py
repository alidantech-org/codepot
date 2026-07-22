"""Inference summary rendering."""

from __future__ import annotations

from cli.presentation.core.tables import render_key_value_table


def render_infer_summary(result) -> None:
    """Render inference summary."""
    summary = {
        "Title": getattr(result, "title", "-"),
        "OpenAPI": getattr(result, "openapi_version", "-"),
        "API Version": getattr(result, "api_version", "-"),
        "Resources": getattr(result, "resources_count", 0),
        "Schemas": getattr(result, "schemas_count", 0),
        "Operations": getattr(result, "operations_count", 0),
        "Dependencies": getattr(result, "dependencies_count", 0),
        "Alias Schemas": getattr(result, "alias_schemas_count", 0),
    }

    for kind, count in getattr(result, "schema_kind_counts", {}).items():
        summary[f"Schema Kind: {kind}"] = count

    render_key_value_table(
        "Inference Summary",
        summary,
        highlight_zero=True,
    )
