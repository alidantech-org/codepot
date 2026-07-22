"""Runtime OpenAPI inspection workflow."""

from __future__ import annotations

from openapi.inspector import inspect_openapi_document
from openapi.loader import load_openapi_document
from app.models import InspectInput, InspectOutput, ResourceSummary, RuntimeDiagnostic, RuntimeEvent


def run_inspect(request: InspectInput) -> InspectOutput:
    """Inspect an OpenAPI document and return structured output."""
    _notify(request, stage="loading_openapi", message="Loading OpenAPI document")
    document = load_openapi_document(request.input_path)

    _notify(request, stage="inspecting_openapi", message="Inspecting OpenAPI document")
    inspection = inspect_openapi_document(document)

    _notify(request, stage="inspection_complete", message="OpenAPI inspection completed")

    return InspectOutput(
        input_path=request.input_path,
        title=str(_value(inspection, "title")),
        openapi_version=str(_value(inspection, "openapi_version")),
        api_version=str(_value(inspection, "api_version")),
        paths_count=_int_value(inspection, "path_count", "paths_count"),
        operations_count=_int_value(inspection, "operation_count", "operations_count"),
        schemas_count=_int_value(inspection, "schema_count", "schemas_count"),
        responses_count=_int_value(inspection, "response_count", "responses_count"),
        request_bodies_count=_int_value(
            inspection,
            "request_body_count",
            "request_bodies_count",
        ),
        parameters_count=_int_value(inspection, "parameter_count", "parameters_count"),
        refs_count=_int_value(inspection, "ref_count", "refs_count"),
        component_refs_count=_int_value(
            inspection,
            "component_ref_count",
            "component_refs_count",
        ),
        missing_component_refs_count=_int_value(
            inspection,
            "missing_component_ref_count",
            "missing_component_refs_count",
        ),
        resources=[
            ResourceSummary(
                name=str(_value(resource, "name")),
                path="/".join(_value(resource, "path", default=[])) or "-",
                operations_count=_int_value(resource, "operation_count", "operations_count"),
            )
            for resource in _items(inspection, "resources")
        ],
        diagnostics=[RuntimeDiagnostic(level="info", message="OpenAPI inspection completed.")],
    )


def _items(value, name: str) -> list:
    result = getattr(value, name, [])
    return list(result or [])


def _value(value, *names: str, default="-"):
    for name in names:
        if hasattr(value, name):
            result = getattr(value, name)
            return default if result is None else result
    return default


def _int_value(value, *names: str) -> int:
    result = _value(value, *names, default=0)
    try:
        return int(result)
    except (TypeError, ValueError):
        return 0


def _notify(
    request: InspectInput,
    *,
    stage: str,
    message: str,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    if request.progress is None:
        return

    request.progress(
        RuntimeEvent(
            stage=stage,
            message=message,
            level=level,
            current=current,
            total=total,
        )
    )
