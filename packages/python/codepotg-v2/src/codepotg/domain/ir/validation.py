from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection, Mapping

from codepotg.diagnostics import Diagnostic, DiagnosticSeverity, Diagnostics, RelatedLocation, SourceSpan

from .base import SemanticId
from .events import Event, OperationEffects
from .facets import AccessFacet, ExecutionFacet, OperationFacets, TriggerFacet, TriggerKind, WorkflowFacets
from .groups import Contract, Group, walk_groups
from .operations import Operation, OperationFailure, OperationOutput
from .schemas import Schema, SchemaUse
from .storage import StorageMapping
from .types import TypeExpression, type_references
from .views import View, walk_views
from .workflows import Workflow, WorkflowStep, WorkflowStepKind, walk_workflow_steps


@dataclass(slots=True)
class _Seen:
    kind: str
    span: SourceSpan | None


@dataclass(slots=True)
class _Index:
    schemas: dict[SemanticId, Schema] = field(default_factory=dict)
    operations: dict[SemanticId, Operation] = field(default_factory=dict)
    views: dict[SemanticId, View] = field(default_factory=dict)
    storage: dict[SemanticId, StorageMapping] = field(default_factory=dict)
    workflows: dict[SemanticId, Workflow] = field(default_factory=dict)
    events: dict[SemanticId, Event] = field(default_factory=dict)
    policies: set[SemanticId] = field(default_factory=set)


class ContractValidator:
    def validate(self, contract: Contract) -> Diagnostics:
        diagnostics: list[Diagnostic] = []
        index = _Index()
        seen: dict[SemanticId, _Seen] = {}
        self._register(seen, contract.id, "contract", _owner_span(contract), diagnostics)

        groups = walk_groups(contract.groups)
        for group in groups:
            self._register_group(group, index, seen, diagnostics)
        for group in groups:
            self._validate_group(group, index, diagnostics)

        return Diagnostics.from_iterable(diagnostics)

    def _register_group(
        self,
        group: Group,
        index: _Index,
        seen: dict[SemanticId, _Seen],
        diagnostics: list[Diagnostic],
    ) -> None:
        self._register(seen, group.id, "group", _owner_span(group), diagnostics)
        for schema in group.schemas:
            self._register(seen, schema.id, "schema", _owner_span(schema), diagnostics)
            index.schemas.setdefault(schema.id, schema)
            for schema_field in schema.fields:
                self._register(
                    seen,
                    schema_field.id,
                    "schema_field",
                    _owner_span(schema_field),
                    diagnostics,
                )
        for operation in group.operations:
            self._register(seen, operation.id, "operation", _owner_span(operation), diagnostics)
            index.operations.setdefault(operation.id, operation)
        for view in walk_views(group.views):
            self._register(seen, view.id, "view", _owner_span(view), diagnostics)
            index.views.setdefault(view.id, view)
        for mapping in group.storage_mappings:
            self._register(seen, mapping.id, "storage_mapping", _owner_span(mapping), diagnostics)
            index.storage.setdefault(mapping.id, mapping)
        for workflow in group.workflows:
            self._register(seen, workflow.id, "workflow", _owner_span(workflow), diagnostics)
            index.workflows.setdefault(workflow.id, workflow)
        for policy in group.policies:
            self._register(seen, policy.id, "policy", _owner_span(policy), diagnostics)
            index.policies.add(policy.id)
        for event in group.events:
            self._register(seen, event.id, "event", _owner_span(event), diagnostics)
            index.events.setdefault(event.id, event)

    def _register(
        self,
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

    def _validate_group(
        self,
        group: Group,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for schema in group.schemas:
            self._validate_schema(schema, index, diagnostics)
        for operation in group.operations:
            self._validate_operation(operation, index, diagnostics)
        for view in walk_views(group.views):
            self._validate_view(view, index, diagnostics)
        for mapping in group.storage_mappings:
            self._validate_storage(mapping, index, diagnostics)
        for workflow in group.workflows:
            self._validate_workflow(workflow, index, diagnostics)
        for event in group.events:
            self._require_schema(event.payload_schema, "event payload", event, index, diagnostics)
            self._require_schema(event.context_schema, "event context", event, index, diagnostics)
        self._validate_access(group.facets.access, group, index, diagnostics)
        self._validate_execution(group.facets.execution, group, index, diagnostics)

    def _validate_schema(
        self,
        schema: Schema,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for schema_field in schema.fields:
            self._validate_type(schema_field.type, schema_field, index, diagnostics)
        if schema.item_type is not None:
            self._validate_type(schema.item_type, schema, index, diagnostics)
        if schema.alias_of is not None:
            self._validate_type(schema.alias_of, schema, index, diagnostics)

    def _validate_type(
        self,
        expression: TypeExpression,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for reference in type_references(expression):
            self._require(reference, index.schemas, "IR_MISSING_SCHEMA", "schema type reference", owner, diagnostics)

    def _validate_operation(
        self,
        operation: Operation,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for item in operation.inputs:
            self._validate_schema_use(item, operation, index, diagnostics)
        for item in operation.outputs:
            self._validate_output(item, operation, index, diagnostics)
        for item in operation.failures:
            self._validate_failure(item, operation, index, diagnostics)
        self._validate_effects(operation.effects, operation, index, diagnostics)
        self._validate_operation_facets(operation.facets, operation, index, diagnostics)

    def _validate_schema_use(
        self,
        schema_use: SchemaUse,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require(schema_use.schema, index.schemas, "IR_MISSING_SCHEMA", "schema use", owner, diagnostics)

    def _validate_output(
        self,
        output: OperationOutput,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require_schema(output.schema, "operation output", owner, index, diagnostics)

    def _validate_failure(
        self,
        failure: OperationFailure,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require_schema(failure.schema, "operation failure", owner, index, diagnostics)

    def _validate_effects(
        self,
        effects: OperationEffects,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for effect in effects.events:
            self._require(effect.event, index.events, "IR_MISSING_EVENT", "emitted event", owner, diagnostics)
            self._require_schema(effect.payload_schema, "event effect payload", owner, index, diagnostics)

    def _validate_operation_facets(
        self,
        facets: OperationFacets,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._validate_access(facets.access, owner, index, diagnostics)
        self._validate_trigger(facets.trigger, owner, index, diagnostics)
        self._validate_execution(facets.execution, owner, index, diagnostics)
        if facets.events is not None:
            for event in facets.events.consumes:
                self._require(event, index.events, "IR_MISSING_EVENT", "consumed event", owner, diagnostics)

    def _validate_access(
        self,
        access: AccessFacet | None,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        if access is None:
            return
        for policy in access.uses + access.inherited + access.effective:
            self._require(policy, index.policies, "IR_MISSING_POLICY", "access policy", owner, diagnostics)

    def _validate_trigger(
        self,
        trigger: TriggerFacet | None,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        if trigger is None:
            return
        if trigger.kind is TriggerKind.EVENT and trigger.event is not None:
            self._require(trigger.event, index.events, "IR_MISSING_EVENT", "event trigger", owner, diagnostics)
        if trigger.kind is TriggerKind.INTERACTION and trigger.view is not None:
            self._require(trigger.view, index.views, "IR_MISSING_VIEW", "interaction trigger view", owner, diagnostics)
        if trigger.kind is TriggerKind.STORAGE and trigger.storage is not None:
            self._require(
                trigger.storage,
                index.storage,
                "IR_MISSING_STORAGE_MAPPING",
                "storage trigger",
                owner,
                diagnostics,
            )

    def _validate_execution(
        self,
        execution: ExecutionFacet | None,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        if execution is None:
            return
        for hook in execution.hooks:
            self._require(
                hook.operation,
                index.operations,
                "IR_MISSING_OPERATION",
                "execution hook operation",
                owner,
                diagnostics,
            )

    def _validate_storage(
        self,
        mapping: StorageMapping,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        schema = index.schemas.get(mapping.schema)
        if schema is None:
            self._require(mapping.schema, index.schemas, "IR_MISSING_SCHEMA", "storage mapping schema", mapping, diagnostics)
            return
        field_ids = {item.id for item in schema.fields}
        for item in mapping.fields:
            self._require(item.field, field_ids, "IR_MISSING_FIELD", "storage field mapping", mapping, diagnostics)
        for item in mapping.primary_key:
            self._require(item, field_ids, "IR_MISSING_FIELD", "storage primary key field", mapping, diagnostics)
        for index_fields in mapping.indexes:
            for item in index_fields:
                self._require(item, field_ids, "IR_MISSING_FIELD", "storage index field", mapping, diagnostics)

    def _validate_view(
        self,
        view: View,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require_schema(view.schema, "view schema", view, index, diagnostics)
        self._validate_access(view.access, view, index, diagnostics)
        for trigger in view.triggers:
            self._require(
                trigger.operation,
                index.operations,
                "IR_MISSING_OPERATION",
                "view trigger operation",
                view,
                diagnostics,
            )
            self._require_schema(trigger.payload_schema, "view trigger payload", view, index, diagnostics)

    def _validate_workflow(
        self,
        workflow: Workflow,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        for item in workflow.inputs:
            self._validate_schema_use(item, workflow, index, diagnostics)
        for item in workflow.outputs:
            self._validate_output(item, workflow, index, diagnostics)
        for item in workflow.failures:
            self._validate_failure(item, workflow, index, diagnostics)
        self._validate_effects(workflow.effects, workflow, index, diagnostics)
        self._validate_workflow_facets(workflow.facets, workflow, index, diagnostics)

        steps = walk_workflow_steps(workflow.steps)
        step_names = {step.name for step in steps}
        for step in steps:
            self._validate_workflow_step(step, workflow, step_names, index, diagnostics)
        for transition in workflow.transitions:
            for label, step_name in (("source", transition.source), ("target", transition.target)):
                if step_name not in step_names:
                    diagnostics.append(
                        _error(
                            "IR_MISSING_WORKFLOW_STEP",
                            f"workflow transition {label} {step_name!r} does not exist",
                            workflow,
                            (("step", step_name),),
                        )
                    )

    def _validate_workflow_facets(
        self,
        facets: WorkflowFacets,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._validate_trigger(facets.trigger, owner, index, diagnostics)
        self._validate_access(facets.access, owner, index, diagnostics)
        self._validate_execution(facets.execution, owner, index, diagnostics)
        if facets.events is not None:
            for event in facets.events.consumes:
                self._require(event, index.events, "IR_MISSING_EVENT", "workflow consumed event", owner, diagnostics)

    def _validate_workflow_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
        step_names: set[str],
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        if step.operation is not None:
            self._require(step.operation, index.operations, "IR_MISSING_OPERATION", "workflow step operation", workflow, diagnostics)
        if step.compensation is not None:
            self._require(
                step.compensation.operation,
                index.operations,
                "IR_MISSING_OPERATION",
                "workflow compensation operation",
                workflow,
                diagnostics,
            )
        if step.wait_event is not None:
            self._require(step.wait_event, index.events, "IR_MISSING_EVENT", "workflow wait event", workflow, diagnostics)
        if step.kind is WorkflowStepKind.DECISION:
            for case in step.decision_cases:
                if case.target not in step_names:
                    diagnostics.append(
                        _error(
                            "IR_MISSING_WORKFLOW_STEP",
                            f"workflow decision target {case.target!r} does not exist",
                            workflow,
                            (("step", case.target),),
                        )
                    )

    def _require_schema(
        self,
        semantic_id: SemanticId | None,
        relation: str,
        owner: object,
        index: _Index,
        diagnostics: list[Diagnostic],
    ) -> None:
        if semantic_id is not None:
            self._require(semantic_id, index.schemas, "IR_MISSING_SCHEMA", relation, owner, diagnostics)

    def _require(
        self,
        semantic_id: SemanticId,
        collection: Collection[SemanticId] | Mapping[SemanticId, object],
        code: str,
        relation: str,
        owner: object,
        diagnostics: list[Diagnostic],
    ) -> None:
        if semantic_id in collection:
            return
        diagnostics.append(
            _error(
                code,
                f"{relation} references missing semantic id {semantic_id}",
                owner,
                (("id", str(semantic_id)), ("relation", relation)),
            )
        )


def validate_contract(contract: Contract) -> Diagnostics:
    return ContractValidator().validate(contract)


def _owner_span(owner: object) -> SourceSpan | None:
    data = getattr(owner, "data", None)
    provenance = getattr(data, "provenance", None)
    return getattr(provenance, "span", None)


def _error(
    code: str,
    message: str,
    owner: object,
    details: tuple[tuple[str, object], ...],
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        span=_owner_span(owner),
        details=tuple(sorted(details, key=lambda item: item[0])),
    )
