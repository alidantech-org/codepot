from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract
from .index import SemanticIndex, owner_span


def validate_presentations(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for presentation in contract.presentations:
        parents = {entry.id: entry.navigation_parent for entry in presentation.entries}
        for entry in presentation.entries:
            seen: set[object] = set()
            current = entry.id
            while current is not None:
                if current in seen:
                    diagnostics.append(Diagnostic(code="IR_PRESENTATION_NAVIGATION_CYCLE", severity=DiagnosticSeverity.ERROR, message=f"presentation {presentation.id} contains a navigation cycle at {current}", span=owner_span(entry)))
                    break
                seen.add(current)
                current = parents.get(current)
            for semantic_id in entry.policies:
                _require(semantic_id, index.policies, "IR_MISSING_POLICY", "presentation policy", entry, diagnostics)
            for semantic_id in entry.operations:
                _require(semantic_id, index.operations, "IR_MISSING_OPERATION", "presentation operation", entry, diagnostics)
            for semantic_id in entry.events:
                _require(semantic_id, index.events, "IR_MISSING_EVENT", "presentation event", entry, diagnostics)
            for semantic_id in entry.workflows:
                _require(semantic_id, index.workflows, "IR_MISSING_WORKFLOW", "presentation workflow", entry, diagnostics)
    return Diagnostics.from_iterable(diagnostics)


def _require(semantic_id: object, collection: object, code: str, relation: str, owner: object, diagnostics: list[Diagnostic]) -> None:
    if semantic_id in collection:  # type: ignore[operator]
        return
    diagnostics.append(Diagnostic(code=code, severity=DiagnosticSeverity.ERROR, message=f"{relation} references missing semantic id {semantic_id}", span=owner_span(owner), details=(("id", str(semantic_id)), ("relation", relation))))


__all__ = ["validate_presentations"]
