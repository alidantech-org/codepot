from __future__ import annotations

from jinja2 import TemplateSyntaxError, meta, nodes
from jinja2.visitor import NodeVisitor

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

    contract_paths = set(request.context_contract.paths)
    allowed_roots = _contract_roots(request.context_contract.paths)
    undeclared_roots = set(meta.find_undeclared_variables(parsed))
    for variable in sorted(undeclared_roots):
        if variable not in allowed_roots:
            diagnostics.append(
                RendererDiagnostic(
                    "JINJA_CONTEXT_NAME",
                    f"template references undeclared context root {variable!r}",
                    path=request.template.resource_id,
                )
            )

    visitor = _StaticAccessVisitor(undeclared_roots & allowed_roots)
    visitor.visit(parsed)
    unknown_paths = {
        path: line
        for path, line in visitor.paths.items()
        if path not in contract_paths
    }
    for path in _deepest_paths(unknown_paths):
        diagnostics.append(
            RendererDiagnostic(
                "JINJA_CONTEXT_PATH",
                f"template references context path not supplied by Dryv: {path}",
                path=request.template.resource_id,
                line=unknown_paths[path],
            )
        )
    return ValidateTemplateResult(request.validation_id, not diagnostics, tuple(diagnostics))


class _StaticAccessVisitor(NodeVisitor):
    def __init__(self, roots: set[str]) -> None:
        self.roots = roots
        self.paths: dict[str, int | None] = {}

    def visit_Getattr(self, node: nodes.Getattr, *args: object, **kwargs: object) -> None:
        self._record(node)
        self.generic_visit(node, *args, **kwargs)

    def visit_Getitem(self, node: nodes.Getitem, *args: object, **kwargs: object) -> None:
        self._record(node)
        self.generic_visit(node, *args, **kwargs)

    def _record(self, node: nodes.Expr) -> None:
        segments = _static_segments(node)
        if segments is None or not segments or segments[0] not in self.roots:
            return
        path = _contract_path(segments)
        line = getattr(node, "lineno", None)
        previous = self.paths.get(path)
        if previous is None or (line is not None and line < previous):
            self.paths[path] = line


def _static_segments(node: nodes.Expr) -> tuple[str, ...] | None:
    if isinstance(node, nodes.Name):
        return (node.name,)
    if isinstance(node, nodes.Getattr):
        parent = _static_segments(node.node)
        return None if parent is None else (*parent, node.attr)
    if isinstance(node, nodes.Getitem):
        parent = _static_segments(node.node)
        if parent is None or not isinstance(node.arg, nodes.Const):
            return None
        value = node.arg.value
        if isinstance(value, int) and not isinstance(value, bool):
            return (*parent, "[*]")
        if isinstance(value, str) and value.isidentifier():
            return (*parent, value)
    return None


def _contract_path(segments: tuple[str, ...]) -> str:
    result = "$"
    for segment in segments:
        if segment == "[*]":
            result += segment
        else:
            result += f".{segment}"
    return result


def _deepest_paths(paths: dict[str, int | None]) -> tuple[str, ...]:
    values = tuple(sorted(paths))
    return tuple(
        path
        for path in values
        if not any(
            other != path
            and (other.startswith(path + ".") or other.startswith(path + "["))
            for other in values
        )
    )


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
