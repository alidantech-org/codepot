from __future__ import annotations

from codepotg.diagnostics import Diagnostic, DiagnosticSeverity


def diagnostic(
    code: str,
    message: str,
    *,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    **details: object,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=severity,
        message=message,
        details=tuple(sorted(details.items())),
    )
