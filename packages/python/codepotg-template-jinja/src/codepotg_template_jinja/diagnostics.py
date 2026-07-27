from __future__ import annotations

import re
from collections.abc import Mapping

from codepotg.diagnostics import (
    Diagnostic,
    DiagnosticSeverity,
    Diagnostics,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
)

_UNDEFINED_NAME = re.compile(r"^'([^']+)' is undefined$")


def error_diagnostic(
    code: str,
    message: str,
    *,
    template_id: str,
    line: int | None = None,
    details: Mapping[str, object] | None = None,
) -> Diagnostic:
    span = None
    if line is not None and line >= 1:
        position = SourcePosition(line=line, column=1)
        span = SourceSpan(
            source=SourceIdentity(SourceKind.TEMPLATE, template_id),
            start=position,
            end=position,
        )
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        span=span,
        details=tuple(sorted((details or {}).items())),
    )


def failure_result_diagnostics(diagnostic: Diagnostic) -> Diagnostics:
    return Diagnostics.from_iterable((diagnostic,))


def undefined_name(message: str) -> str | None:
    match = _UNDEFINED_NAME.fullmatch(message)
    return match.group(1) if match is not None else None
