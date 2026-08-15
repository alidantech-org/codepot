from __future__ import annotations

from collections.abc import Collection, Mapping

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from ..base import SemanticId
from ..events import OperationEffects
from ..facets import (
    AccessFacet,
    ExecutionFacet,
    OperationFacets,
    TriggerFacet,
    TriggerKind,
    WorkflowFacets,
)
from ..groups import Contract, Group, walk_groups
from ..operations import Operation, OperationFailure, OperationOutput
from ..schemas import Schema, SchemaUse
from ..storage import StorageMapping
from ..types import TypeExpression, type_references
from ..views import View, walk_views
from ..workflows import (
    Workflow,
    WorkflowStep,
    WorkflowStepKind,
    walk_workflow_steps,
)
from .index import SemanticIndex, owner_span


class ContractValidator:
    def validate(self, contract: Contract) -> Diagnostics:
        index, index_diagnostics = SemanticIndex.build(contract)
        diagnostics = list(index_diagnostics.items)

        for group in walk_groups(contract.groups):
            self._validate_group(group, index, diagnostics)

        return Diagnostics.from_iterable(diagnostics)

    def _validate_group(
        self,
        group: Group,
        index: SemanticIndex,
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
        index: SemanticIndex,
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
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        for reference in type_references(expression):
            self._require(
                reference,
                index.schemas,
                "IR_MISSING_SCHEMA",
                "schema type reference",
                owner,
                diagnostics,
            )

    def _validate_operation(
        self,
        operation: Operation,
        index: SemanticIndex,
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
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require(
            schema_use.schema,
            index.schemas,
            "IR_MISSING_SCHEMA",
            "schema use",
            owner,
            diagnostics,
        )

    def _validate_output(
        self,
        output: OperationOutput,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require_schema(output.schema, "operation output", owner, index, diagnostics)

    def _validate_failure(
        self,
        failure: OperationFailure,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._require_schema(failure.schema, "operation failure", owner, index, diagnostics)

    def _validate_effects(
        self,
        effects: OperationEffects,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        for effect in effects.events:
            self._require(
                effect.event,
                index.events,
                "IR_MISSING_EVENT",
                "emitted event",
                owner,
                diagnostics,
            )
            self._require_schema(
                effect.payload_schema,
                "event effect payload",
                owner,
                index,
                diagnostics,
            )

    def _validate_operation_facets(
        self,
        facets: OperationFacets,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._validate_access(facets.access, owner, index, diagnostics)
        self._validate_trigger(facets.trigger, owner, index, diagnostics)
        self._validate_execution(facets.execution, owner, index, diagnostics)
        if facets.events is not None:
            for event in facets.events.consumes:
                self._require(
                    event,
                    index.events,
                    "IR_MISSING_EVENT",
                    "consumed event",
                    owner,
                    diagnostics,
                )

    def _validate_access(
        self,
        access: AccessFacet | None,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        if access is None:
            return
        for policy in access.uses + access.inherited + access.effective:
            self._require(
                policy,
                index.policies,
                "IR_MISSING_POLICY",
                "access policy",
                owner,
                diagnostics,
            )

    def _validate_trigger(
        self,
        trigger: TriggerFacet | None,
        owner: object,
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        if trigger is None:
            return
        if trigger.kind is TriggerKind.EVENT and trigger.event is not None:
            self._require(
                trigger.event,
                index.events,
                "IR_MISSING_EVENT",
                "event trigger",
                owner,
                diagnostics,
            )
        if trigger.kind is TriggerKind.INTERACTION and trigger.view is not None:
            self._require(
                trigger.view,
                index.views,
                "IR_MISSING_VIEW",
                "interaction trigger view",
                owner,
                diagnostics,
            )
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
        index: SemanticIndex,
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
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        schema = index.schemas.get(mapping.schema)
        if schema is None:
            self._require(
                mapping.schema,
                index.schemas,
                "IR_MISSING_SCHEMA",
                "storage mapping schema",
                mapping,
                diagnostics,
            )
            return

        field_ids = {item.id for item in schema.fields}
        for item in mapping.fields:
            self._require(
                item.field,
                field_ids,
                "IR_MISSING_FIELD",
                "storage field mapping",
                mapping,
                diagnostics,
            )
        for item in mapping.primary_key:
            self._require(
                item,
                field_ids,
                "IR_MISSING_FIELD",
                "storage primary key field",
                mapping,
                diagnostics,
            )
        for index_fields in mapping.indexes:
            for item in index_fields:
                self._require(
                    item,
                    field_ids,
                    "IR_MISSING_FIELD",
                    "storage index field",
                    mapping,
                    diagnostics,
                )

    def _validate_view(
        self,
        view: View,
        index: SemanticIndex,
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
            self._require_schema(
                trigger.payload_schema,
                "view trigger payload",
                view,
                index,
                diagnostics,
            )

    def _validate_workflow(
        self,
        workflow: Workflow,
        index: SemanticIndex,
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
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        self._validate_trigger(facets.trigger, owner, index, diagnostics)
        self._validate_access(facets.access, owner, index, diagnostics)
        self._validate_execution(facets.execution, owner, index, diagnostics)
        if facets.events is not None:
            for event in facets.events.consumes:
                self._require(
                    event,
                    index.events,
                    "IR_MISSING_EVENT",
                    "workflow consumed event",
                    owner,
                    diagnostics,
                )

    def _validate_workflow_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
        step_names: set[str],
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        if step.operation is not None:
            self._require(
                step.operation,
                index.operations,
                "IR_MISSING_OPERATION",
                "workflow step operation",
                workflow,
                diagnostics,
            )
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
            self._require(
                step.wait_event,
                index.events,
                "IR_MISSING_EVENT",
                "workflow wait event",
                workflow,
                diagnostics,
            )
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
        index: SemanticIndex,
        diagnostics: list[Diagnostic],
    ) -> None:
        if semantic_id is not None:
            self._require(
                semantic_id,
                index.schemas,
                "IR_MISSING_SCHEMA",
                relation,
                owner,
                diagnostics,
            )

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
        span=owner_span(owner),
        details=tuple(sorted(details, key=lambda item: item[0])),
    )
