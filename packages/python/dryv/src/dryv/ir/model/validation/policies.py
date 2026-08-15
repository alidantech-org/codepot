from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..base import SemanticId
from ..groups import Contract, walk_groups
from .index import SemanticIndex, owner_span


def validate_policy_event_relationships(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    graph: dict[SemanticId, tuple[SemanticId, ...]] = {}

    for group in walk_groups(contract.groups):
        for policy in group.policies:
            graph[policy.id] = policy.policies
            if policy.context_schema is not None and policy.context_schema not in index.schemas:
                diagnostics.append(
                    Diagnostic(
                        code="IR_MISSING_SCHEMA",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"policy {policy.id} references missing context schema {policy.context_schema}",
                        span=owner_span(policy),
                        details=(("id", str(policy.context_schema)), ("relation", "policy context schema")),
                    )
                )
            for composed in policy.policies:
                if composed not in index.policies:
                    diagnostics.append(
                        Diagnostic(
                            code="IR_MISSING_POLICY",
                            severity=DiagnosticSeverity.ERROR,
                            message=f"policy {policy.id} composes missing policy {composed}",
                            span=owner_span(policy),
                            details=(("id", str(composed)), ("relation", "composed policy")),
                        )
                    )
        for event in group.events:
            for policy_id in event.policies:
                if policy_id not in index.policies:
                    diagnostics.append(
                        Diagnostic(
                            code="IR_MISSING_POLICY",
                            severity=DiagnosticSeverity.ERROR,
                            message=f"event {event.id} references missing policy {policy_id}",
                            span=owner_span(event),
                            details=(("id", str(policy_id)), ("relation", "event policy")),
                        )
                    )

    diagnostics.extend(_policy_cycle_diagnostics(graph, index))
    return Diagnostics.from_iterable(diagnostics)


def _policy_cycle_diagnostics(
    graph: dict[SemanticId, tuple[SemanticId, ...]],
    index: SemanticIndex,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    active: list[SemanticId] = []
    finished: set[SemanticId] = set()
    reported: set[tuple[SemanticId, ...]] = set()

    def visit(policy_id: SemanticId) -> None:
        if policy_id in finished:
            return
        if policy_id in active:
            start = active.index(policy_id)
            cycle = tuple((*active[start:], policy_id))
            key = tuple(sorted(set(cycle[:-1]), key=str))
            if key not in reported:
                reported.add(key)
                owner = index.policies.get(policy_id)
                diagnostics.append(
                    Diagnostic(
                        code="IR_POLICY_CYCLE",
                        severity=DiagnosticSeverity.ERROR,
                        message="policy composition cycle: " + " -> ".join(str(item) for item in cycle),
                        span=owner_span(owner) if owner is not None else None,
                    )
                )
            return
        active.append(policy_id)
        try:
            for child in graph.get(policy_id, ()):
                if child in graph:
                    visit(child)
        finally:
            active.pop()
        finished.add(policy_id)

    for policy_id in sorted(graph, key=str):
        visit(policy_id)
    return diagnostics


__all__ = ["validate_policy_event_relationships"]
