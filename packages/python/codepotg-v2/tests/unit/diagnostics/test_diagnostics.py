from __future__ import annotations

from codepotg.diagnostics import (
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
)


def test_diagnostics_are_immutable_serializable_and_sorted() -> None:
    span = SourceSpan(
        source=SourceIdentity(SourceKind.FILE, "contract.yaml"),
        start=SourcePosition(2, 3, 10),
        end=SourcePosition(2, 9, 16),
    )
    warning = Diagnostic(
        code="CFG_DEPRECATED",
        severity=DiagnosticSeverity.WARNING,
        message="deprecated field",
        span=span,
    )
    error = Diagnostic(
        code="CFG_UNKNOWN_FIELD",
        severity=DiagnosticSeverity.ERROR,
        message="unknown field",
        span=span,
        details=(("field", "languages"),),
        suggestion="remove the unsupported field",
    )

    diagnostics = Diagnostics.from_iterable((warning, error))

    assert diagnostics.has_errors
    assert diagnostics.errors == (error,)
    assert diagnostics.items == (error, warning)
    assert diagnostics.to_dict()[0]["span"] == {
        "source": {"kind": "file", "value": "contract.yaml"},
        "start": {"line": 2, "column": 3, "offset": 10},
        "end": {"line": 2, "column": 9, "offset": 16},
    }
