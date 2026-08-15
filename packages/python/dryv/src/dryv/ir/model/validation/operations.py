from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..base import SemanticId
from ..groups import Contract, walk_groups
from .index import SemanticIndex, owner_span


def validate_operation_relationships(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    requires_graph: dict[SemanticId, tuple[SemanticId, ...]] = {}
    delegate_graph: dict[SemanticId, tuple[SemanticId, ...]] = {}
    order_graph: dict[SemanticId, list[SemanticId]] = {}

    for group in walk_groups(contract.groups):
        for operation in group.operations:
            requires_graph[operation.id] = operation.relations.requires
            delegate_graph[operation.id] = operation.relations.delegates_to
            order_graph.setdefault(operation.id, [])

            for schema_id in operation.subjects:
                _require(schema_id, index.schemas, "IR_MISSING_SCHEMA", "operation subject", operation, diagnostics)
            for policy_id in operation.policies:
                _require(policy_id, index.policies, "IR_MISSING_POLICY", "operation policy", operation, diagnostics)

            for relation, values in (
                ("invokes", operation.relations.invokes),
                ("requires", operation.relations.requires),
                ("delegates", operation.relations.delegates_to),
                ("runs before", operation.relations.before),
                ("runs after", operation.relations.after),
            ):
                for target in values:
                    _require(target, index.operations, "IR_MISSING_OPERATION", f"operation {relation}", operation, diagnostics)

            for workflow_id in operation.relations.triggers_workflows:
                _require(workflow_id, index.workflows, "IR_MISSING_WORKFLOW", "operation triggered workflow", operation, diagnostics)

            for target in operation.relations.before:
                if target in index.operations:
                    order_graph.setdefault(operation.id, []).append(target)
            for source in operation.relations.after:
                if source in index.operations:
                    order_graph.setdefault(source, []).append(operation.id)

    diagnostics.extend(_cycle_diagnostics(requires_graph, index, "IR_OPERATION_REQUIREMENT_CYCLE", "operation requirement cycle"))
    diagnostics.extend(_cycle_diagnostics(delegate_graph, index, "IR_OPERATION_DELEGATION_CYCLE", "operation delegation cycle"))
    diagnostics.extend(_cycle_diagnostics({key: tuple(value) for key, value in order_graph.items()}, index, "IR_OPERATION_ORDER_CYCLE", "operation ordering cycle"))
    return Diagnostics.from_iterable(diagnostics)


def _require(
    semantic_id: SemanticId,
    collection: object,
    code: str,
    relation: str,
    owner: object,
    diagnostics: list[Diagnostic],
) -> None:
    if semantic_id in collection:  # type: ignore[operator]
        return
    diagnostics.append(
        Diagnostic(
            code=code,
            severity=DiagnosticSeverity.ERROR,
            message=f"{relation} references missing semantic id {semantic_id}",
            span=owner_span(owner),
            details=(("id", str(semantic_id)), ("relation", relation)),
        )
    )


def _cycle_diagnostics(
    graph: dict[SemanticId, tuple[SemanticId, ...]],
    index: SemanticIndex,
    code: str,
    label: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    active: list[SemanticId] = []
    finished: set[SemanticId] = set()
    reported: set[tuple[SemanticId, ...]] = set()

    def visit(operation_id: SemanticId) -> None:
        if operation_id in finished:
            return
        if operation_id in active:
            start = active.index(operation_id)
            cycle = tuple((*active[start:], operation_id))
            key = tuple(sorted(set(cycle[:-1]), key=str))
            if key not in reported:
                reported.add(key)
                owner = index.operations.get(operation_id)
                diagnostics.append(
                    Diagnostic(
                        code=code,
                        severity=DiagnosticSeverity.ERROR,
                        message=label + ": " + " -> ".join(str(item) for item in cycle),
                        span=owner_span(owner) if owner is not None else None,
                    )
                )
            return
        active.append(operation_id)
        try:
            for child in graph.get(operation_id, ()):
                if child in graph:
                    visit(child)
        finally:
            active.pop()
        finished.add(operation_id)

    for operation_id in sorted(graph, key=str):
        visit(operation_id)
    return diagnostics


__all__ = ["validate_operation_relationships"]
