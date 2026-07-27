from __future__ import annotations

from collections.abc import Mapping

from codepotg.diagnostics import SourceSpan

from ..diagnostics import DiagnosticBag


def validate_structure(
    value: dict[str, object],
    spans: Mapping[str, SourceSpan],
    diagnostics: DiagnosticBag,
) -> str | None:
    version = value.get("openapi")
    if not isinstance(version, str):
        diagnostics.error(
            "OA_STRUCTURE_VERSION",
            "OpenAPI root requires a string 'openapi' version",
            span=spans.get("/openapi") or spans.get(""),
        )
        return None
    if not (version.startswith("3.0.") or version.startswith("3.1.")):
        diagnostics.error(
            "OA_UNSUPPORTED_VERSION",
            f"OpenAPI version {version!r} is not supported; expected 3.0.x or 3.1.x",
            span=spans.get("/openapi") or spans.get(""),
        )
        return None

    info = value.get("info")
    if not isinstance(info, dict):
        diagnostics.error(
            "OA_STRUCTURE_INFO",
            "OpenAPI root requires an info object",
            span=spans.get("/info") or spans.get(""),
        )
        return None
    for key in ("title", "version"):
        if not isinstance(info.get(key), str) or not str(info[key]).strip():
            diagnostics.error(
                "OA_STRUCTURE_INFO_FIELD",
                f"OpenAPI info.{key} must be a non-empty string",
                span=spans.get(f"/info/{key}") or spans.get("/info"),
            )

    paths = value.get("paths")
    if paths is None:
        value["paths"] = {}
    elif not isinstance(paths, dict):
        diagnostics.error(
            "OA_STRUCTURE_PATHS",
            "OpenAPI paths must be an object",
            span=spans.get("/paths") or spans.get(""),
        )

    components = value.get("components")
    if components is not None and not isinstance(components, dict):
        diagnostics.error(
            "OA_STRUCTURE_COMPONENTS",
            "OpenAPI components must be an object",
            span=spans.get("/components") or spans.get(""),
        )
    return version if not diagnostics.has_errors else None
