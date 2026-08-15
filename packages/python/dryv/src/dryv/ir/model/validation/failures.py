from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from .index import SemanticIndex, owner_span


def validate_failures(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        codes: set[str] = set()
        for failure in group.failures:
            if failure.code in codes:
                diagnostics.append(Diagnostic(code="IR_DUPLICATE_FAILURE_CODE", severity=DiagnosticSeverity.ERROR, message=f"failure code {failure.code!r} is duplicated in group {group.id}", span=owner_span(failure)))
            codes.add(failure.code)
            if failure.schema is not None and failure.schema not in index.schemas:
                diagnostics.append(Diagnostic(code="IR_MISSING_SCHEMA", severity=DiagnosticSeverity.ERROR, message=f"failure {failure.id} references missing schema {failure.schema}", span=owner_span(failure)))
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_failures"]
