from __future__ import annotations

import pytest

from codepotg.api import (
    CancellationToken,
    OperationCancelled,
    OperationResult,
    OperationStatus,
)
from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity


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
