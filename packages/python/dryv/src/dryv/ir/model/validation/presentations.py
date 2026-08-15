from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract
from .index import owner_span


def validate_presentation_graphs(contract: Contract) -> Diagnostics:
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
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_presentation_graphs"]
