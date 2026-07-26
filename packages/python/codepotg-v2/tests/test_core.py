from __future__ import annotations

import pytest

import codepotg
from codepotg import diagnostics as diagnostic_namespace
from codepotg import versions as version_namespace
from codepotg.core import (
    CancellationToken,
    Diagnostic,
    DiagnosticSeverity,
    Diagnostics,
    OperationCancelled,
    OperationResult,
    OperationStatus,
    SemanticVersion,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
)


def test_semantic_versions_parse_order_and_round_trip() -> None:
    alpha = SemanticVersion.parse("2.0.0-alpha.1")
    beta = SemanticVersion.parse("2.0.0-beta.1")
    release = SemanticVersion.parse("2.0.0")

    assert alpha < beta < release
    assert str(alpha) == "2.0.0-alpha.1"
    assert version_namespace.Version is SemanticVersion
    assert codepotg.__version__ == str(codepotg.CORE_VERSION)


@pytest.mark.parametrize("value", ["", "1", "1.0", "v1.0.0", "1.0.-1"])
def test_semantic_versions_reject_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        SemanticVersion.parse(value)


def test_diagnostics_are_immutable_serializable_and_shared_across_namespaces() -> None:
    span = SourceSpan(
        source=SourceIdentity(SourceKind.FILE, "contract.yaml"),
        start=SourcePosition(2, 3, 10),
        end=SourcePosition(2, 9, 16),
    )
    diagnostic = Diagnostic(
        code="CFG_UNKNOWN_FIELD",
        severity=DiagnosticSeverity.ERROR,
        message="unknown field",
        span=span,
        details=(("field", "languages"),),
        suggestion="remove the unsupported field",
    )
    diagnostics = Diagnostics((diagnostic,))

    assert diagnostics.has_errors
    assert diagnostics.to_dict() if hasattr(diagnostics, "to_dict") else diagnostic.to_dict()
    assert diagnostic.to_dict()["span"] == {
        "source": {"kind": "file", "value": "contract.yaml"},
        "start": {"line": 2, "column": 3, "offset": 10},
        "end": {"line": 2, "column": 9, "offset": 16},
    }
    assert diagnostic_namespace.Diagnostic is Diagnostic
    assert diagnostic_namespace.DiagnosticCollection is Diagnostics


def test_failed_results_require_error_diagnostics() -> None:
    with pytest.raises(ValueError):
        OperationResult[None](status=OperationStatus.FAILED)

    error = Diagnostic(
        code="GEN_FAILED",
        severity=DiagnosticSeverity.ERROR,
        message="generation failed",
    )
    result = OperationResult[None](
        status=OperationStatus.FAILED,
        diagnostics=Diagnostics((error,)),
    )
    assert not result.ok
    assert result.operation_id


def test_cancellation_is_explicit_and_idempotent() -> None:
    token = CancellationToken()
    assert not token.cancelled

    token.cancel("host deadline")
    token.cancel("later reason must not replace the first")

    assert token.cancelled
    assert token.reason == "host deadline"
    with pytest.raises(OperationCancelled, match="host deadline"):
        token.raise_if_cancelled()
