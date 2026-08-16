from __future__ import annotations

from dryv.ir.diagnostics import Diagnostic, DiagnosticSeverity

from dryv_author.core import Declaration


def author_error(code: str, message: str, declaration: Declaration | None = None) -> Diagnostic:
    details: tuple[tuple[str, object], ...] = ()
    if declaration is not None:
        details = (("declaration", declaration.id), ("kind", declaration.kind.value), ("owner", declaration.owner_id))
    return Diagnostic(code, DiagnosticSeverity.ERROR, message, details=details)


__all__ = ["author_error"]
