"""Runtime OpenAPI validation workflow."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openapi.loader import load_openapi_document
from app.models import RuntimeDiagnostic, RuntimeEvent, ValidateInput, ValidateOutput


def run_validate(request: ValidateInput) -> ValidateOutput:
    """Validate an OpenAPI document and return structured output."""
    errors: list[str] = []
    warnings: list[str] = []

    _notify(request, stage="loading_openapi", message="Loading OpenAPI document")

    try:
        loaded_document = load_openapi_document(request.input_path)
    except Exception as exc:
        return ValidateOutput(
            input_path=request.input_path,
            valid=False,
            errors=[str(exc)],
            diagnostics=[
                RuntimeDiagnostic(
                    level="error",
                    message="Failed to load OpenAPI document.",
                    details={"error": str(exc)},
                )
            ],
        )

    document = _unwrap_document(loaded_document)

    _notify(request, stage="validating_openapi", message="Validating OpenAPI document")

    _validate_required_root_fields(document, errors)
    _validate_supported_openapi_version(document, warnings)

    valid = not errors

    _notify(
        request,
        stage="validation_complete",
        message="OpenAPI validation completed",
        level="info" if valid else "error",
    )

    return ValidateOutput(
        input_path=request.input_path,
        valid=valid,
        errors=errors,
        warnings=warnings,
        diagnostics=[
            RuntimeDiagnostic(
                level="info" if valid else "error",
                message="OpenAPI validation completed.",
                details={
                    "openapi": _value(document, "openapi", default="-"),
                    "title": _nested_value(document, ("info", "title"), default="-"),
                    "version": _nested_value(document, ("info", "version"), default="-"),
                },
            )
        ],
    )


def _unwrap_document(document: Any) -> Any:
    """Return the OpenAPI root object from known loader wrapper shapes."""
    if isinstance(document, Mapping):
        return document

    for attr in ("raw", "data", "document", "content", "spec"):
        value = getattr(document, attr, None)
        if isinstance(value, Mapping):
            return value

    return document


def _validate_required_root_fields(document: Any, errors: list[str]) -> None:
    """Validate required OpenAPI root fields."""
    for field in ("openapi", "info", "paths"):
        if not _has_field(document, field):
            errors.append(f"Missing required OpenAPI root field: {field}")


def _validate_supported_openapi_version(document: Any, warnings: list[str]) -> None:
    """Warn for OpenAPI versions outside the expected 3.x range."""
    version = _value(document, "openapi", default="")

    if not str(version).startswith("3."):
        warnings.append(f"Expected OpenAPI 3.x document, got: {version or '-'}")


def _has_field(document: Any, field: str) -> bool:
    value = _value(document, field, default=None)
    return value is not None


def _value(document: Any, field: str, default: Any = "-") -> Any:
    if isinstance(document, Mapping):
        return document.get(field, default)

    return getattr(document, field, default)


def _nested_value(document: Any, path: tuple[str, ...], default: Any = "-") -> Any:
    current = document

    for part in path:
        current = _value(current, part, default=None)
        if current is None:
            return default

    return current


def _notify(
    request: ValidateInput,
    *,
    stage: str,
    message: str,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    """Emit a runtime progress event when a sink is provided."""
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
