from __future__ import annotations

from dryv.ir.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..groups import Contract, walk_groups
from ..views import walk_views
from .index import SemanticIndex, owner_span


def validate_view_relationships(contract: Contract, index: SemanticIndex) -> Diagnostics:
    diagnostics: list[Diagnostic] = []
    for group in walk_groups(contract.groups):
        for view in walk_views(group.views):
            for schema_id in view.schemas:
                _require(schema_id, index.schemas, "IR_MISSING_SCHEMA", "view schema", view, diagnostics)
            for field_id in view.fields:
                _require(field_id, index.fields, "IR_MISSING_FIELD", "view field", view, diagnostics)
            for source_id in view.value_sources:
                _require(source_id, index.value_sources, "IR_MISSING_VALUE_SOURCE", "view value source", view, diagnostics)
            for trigger in view.workflow_triggers:
                _require(trigger.workflow, index.workflows, "IR_MISSING_WORKFLOW", "view workflow trigger", view, diagnostics)
                if trigger.payload_schema is not None:
                    _require(trigger.payload_schema, index.schemas, "IR_MISSING_SCHEMA", "view workflow trigger payload", view, diagnostics)
            for reaction in view.event_reactions:
                _require(reaction.event, index.events, "IR_MISSING_EVENT", "view event reaction", view, diagnostics)
                if reaction.payload_schema is not None:
                    _require(reaction.payload_schema, index.schemas, "IR_MISSING_SCHEMA", "view event reaction payload", view, diagnostics)
            for connection in view.connections:
                _require(connection.target, index.views, "IR_MISSING_VIEW", "view connection", view, diagnostics)
    return Diagnostics.from_iterable(diagnostics)


def _require(value: object, collection: object, code: str, relation: str, owner: object, diagnostics: list[Diagnostic]) -> None:
    if value in collection:  # type: ignore[operator]
        return
    diagnostics.append(Diagnostic(code=code, severity=DiagnosticSeverity.ERROR, message=f"{relation} references missing semantic id {value}", span=owner_span(owner), details=(("id", str(value)), ("relation", relation))))


__all__ = ["validate_view_relationships"]
