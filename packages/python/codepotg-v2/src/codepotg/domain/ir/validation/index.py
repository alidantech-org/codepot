from __future__ import annotations

from dataclasses import dataclass, field

from codepotg.diagnostics import (
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    RelatedLocation,
    SourceSpan,
)

from ..base import SemanticId
from ..events import Event
from ..groups import Contract, walk_groups
from ..operations import Operation
from ..policies import Policy
from ..schemas import Schema
from ..storage import StorageMapping
from ..views import View, walk_views
from ..workflows import Workflow


@dataclass(slots=True)
class _Seen:
    kind: str
    span: SourceSpan | None


@dataclass(slots=True)
class SemanticIndex:
    schemas: dict[SemanticId, Schema] = field(default_factory=dict)
    operations: dict[SemanticId, Operation] = field(default_factory=dict)
    views: dict[SemanticId, View] = field(default_factory=dict)
    storage: dict[SemanticId, StorageMapping] = field(default_factory=dict)
    workflows: dict[SemanticId, Workflow] = field(default_factory=dict)
    events: dict[SemanticId, Event] = field(default_factory=dict)
    policies: dict[SemanticId, Policy] = field(default_factory=dict)

    @classmethod
    def build(cls, contract: Contract) -> tuple[SemanticIndex, Diagnostics]:
        index = cls()
        seen: dict[SemanticId, _Seen] = {}
        diagnostics: list[Diagnostic] = []
        _register(seen, contract.id, "contract", _owner_span(contract), diagnostics)

        for group in walk_groups(contract.groups):
            _register(seen, group.id, "group", _owner_span(group), diagnostics)
            for schema in group.schemas:
                _register(seen, schema.id, "schema", _owner_span(schema), diagnostics)
                index.schemas.setdefault(schema.id, schema)
                for schema_field in schema.fields:
                    _register(
                        seen,
                        schema_field.id,
                        "schema_field",
                        _owner_span(schema_field),
                        diagnostics,
                    )
            for operation in group.operations:
                _register(seen, operation.id, "operation", _owner_span(operation), diagnostics)
                index.operations.setdefault(operation.id, operation)
            for view in walk_views(group.views):
                _register(seen, view.id, "view", _owner_span(view), diagnostics)
                index.views.setdefault(view.id, view)
            for mapping in group.storage_mappings:
                _register(
                    seen,
                    mapping.id,
                    "storage_mapping",
                    _owner_span(mapping),
                    diagnostics,
                )
                index.storage.setdefault(mapping.id, mapping)
            for workflow in group.workflows:
                _register(seen, workflow.id, "workflow", _owner_span(workflow), diagnostics)
                index.workflows.setdefault(workflow.id, workflow)
            for policy in group.policies:
                _register(seen, policy.id, "policy", _owner_span(policy), diagnostics)
                index.policies.setdefault(policy.id, policy)
            for event in group.events:
                _register(seen, event.id, "event", _owner_span(event), diagnostics)
                index.events.setdefault(event.id, event)

        return index, Diagnostics.from_iterable(diagnostics)


def owner_span(owner: object) -> SourceSpan | None:
    return _owner_span(owner)


def _register(
    seen: dict[SemanticId, _Seen],
    semantic_id: SemanticId,
    kind: str,
    span: SourceSpan | None,
    diagnostics: list[Diagnostic],
) -> None:
    previous = seen.get(semantic_id)
    if previous is None:
        seen[semantic_id] = _Seen(kind, span)
        return
    related = (
        (RelatedLocation(f"first declared as {previous.kind}", previous.span),)
        if previous.span is not None
        else ()
    )
    diagnostics.append(
        Diagnostic(
            code="IR_DUPLICATE_ID",
            severity=DiagnosticSeverity.ERROR,
            message=f"semantic id {semantic_id} is declared more than once",
            span=span,
            related=related,
            details=(("id", str(semantic_id)), ("kind", kind)),
            suggestion="assign a stable unique semantic id",
        )
    )


def _owner_span(owner: object) -> SourceSpan | None:
    data = getattr(owner, "data", None)
    provenance = getattr(data, "provenance", None)
    return getattr(provenance, "span", None)
