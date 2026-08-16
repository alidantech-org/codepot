from __future__ import annotations

from jinja2 import TemplateSyntaxError, meta

from dryv_api.renderers import RendererDiagnostic, ValidateTemplateRequest, ValidateTemplateResult

from .environment import create_environment
from .fingerprint import RENDERER_CAPABILITY

_TEMPLATE_MEDIA_TYPES = {
    "text/x-jinja-template",
    "application/x-jinja-template",
    "text/x-jinja",
}


def validate_template(request: ValidateTemplateRequest) -> ValidateTemplateResult:
    diagnostics: list[RendererDiagnostic] = []
    if request.capability != RENDERER_CAPABILITY:
        diagnostics.append(
            RendererDiagnostic(
                "JINJA_CAPABILITY",
                f"unsupported renderer capability {request.capability!r}",
            )
        )
    if request.template.media_type not in _TEMPLATE_MEDIA_TYPES:
        diagnostics.append(
            RendererDiagnostic(
                "JINJA_MEDIA_TYPE",
                f"unsupported Jinja template media type {request.template.media_type!r}",
            )
        )
    try:
        source = request.template.content.decode("utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            RendererDiagnostic(
                "JINJA_TEMPLATE_UTF8",
                "Jinja templates must be UTF-8",
                line=exc.start + 1,
            )
        )
        return ValidateTemplateResult(request.validation_id, False, tuple(diagnostics))
    if diagnostics:
        return ValidateTemplateResult(request.validation_id, False, tuple(diagnostics))

    environment = create_environment()
    try:
        parsed = environment.parse(source)
    except TemplateSyntaxError as exc:
        diagnostics.append(
            RendererDiagnostic(
                "JINJA_TEMPLATE_SYNTAX",
                exc.message,
                path=request.template.resource_id,
                line=exc.lineno,
            )
        )
        return ValidateTemplateResult(request.validation_id, False, tuple(diagnostics))

    allowed_roots = _contract_roots(request.context_contract.paths)
    for variable in sorted(meta.find_undeclared_variables(parsed)):
        if variable not in allowed_roots:
            diagnostics.append(
                RendererDiagnostic(
                    "JINJA_CONTEXT_NAME",
                    f"template references undeclared context root {variable!r}",
                    path=request.template.resource_id,
                )
            )
    return ValidateTemplateResult(request.validation_id, not diagnostics, tuple(diagnostics))


def _contract_roots(paths: tuple[str, ...]) -> set[str]:
    roots: set[str] = set()
    for path in paths:
        clean = path.lstrip("$./")
        if not clean:
            continue
        root = clean.split(".", 1)[0].split("/", 1)[0]
        if root:
            roots.add(root)
    return roots


__all__ = ["validate_template"]
