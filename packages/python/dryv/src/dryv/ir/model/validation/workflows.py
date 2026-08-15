from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..base import SemanticId
from ..groups import Contract
from ..workflows import walk_workflow_steps
from .index import SemanticIndex, owner_span


def validate_workflow_graphs(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    graph: dict[SemanticId, tuple[SemanticId, ...]] = {}
    owners: dict[SemanticId, object] = {}
    for workflow in contract.workflows:
        owners[workflow.id] = workflow
        graph[workflow.id] = tuple(
            step.workflow
            for step in walk_workflow_steps(workflow.steps)
            if step.workflow is not None
        )

    visiting: list[SemanticId] = []
    visited: set[SemanticId] = set()

    def visit(workflow_id: SemanticId) -> None:
        if workflow_id in visited:
            return
        if workflow_id in visiting:
            start = visiting.index(workflow_id)
            cycle = (*visiting[start:], workflow_id)
            owner = owners.get(workflow_id)
            diagnostics.append(
                Diagnostic(
                    code="IR_WORKFLOW_CYCLE",
                    severity=DiagnosticSeverity.ERROR,
                    message="child workflow cycle: "
                    + " -> ".join(str(item) for item in cycle),
                    span=owner_span(owner) if owner is not None else None,
                )
            )
            return
        visiting.append(workflow_id)
        try:
            for child in graph.get(workflow_id, ()):
                if child in index.workflows:
                    visit(child)
        finally:
            visiting.pop()
        visited.add(workflow_id)

    for workflow_id in sorted(graph, key=str):
        visit(workflow_id)
    return Diagnostics.from_iterable(diagnostics)


__all__ = ["validate_workflow_graphs"]
