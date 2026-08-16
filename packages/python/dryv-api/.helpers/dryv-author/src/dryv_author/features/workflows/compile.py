from __future__ import annotations

from dryv.ir import Compensation, EventEffect, Name, OperationEffects, OperationOutput, SchemaUse, SemanticId, Workflow, WorkflowDecisionCase, WorkflowFacets, WorkflowStep, WorkflowStepKind, WorkflowTransition

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import CompensationDeclaration, WorkflowDeclaration, WorkflowStepDeclaration


def compile_workflow(context: CompilerContext, declaration: Declaration) -> Workflow:
    source = context.payload(declaration, WorkflowDeclaration)
    return Workflow(id=SemanticId(declaration.id), name=Name(declaration.name), inputs=tuple(SchemaUse(Name(item.name), context.semantic_id(item.schema), item.required, item.nullable, item.readonly) for item in source.inputs), outputs=tuple(OperationOutput(Name(item.name) if item.name else None, context.semantic_id(item.schema) if item.schema else None, item.optional) for item in source.outputs), steps=tuple(_compile_step(context, item) for item in source.steps), transitions=tuple(WorkflowTransition(item.source, item.target, item.condition) for item in source.transitions), failures=tuple(context.semantic_id(item) for item in source.failures), effects=OperationEffects(tuple(EventEffect(context.semantic_id(item)) for item in source.emitted_events)), facets=WorkflowFacets(durable=source.durable, timeout_seconds=source.timeout_seconds), compensation_order=source.compensation_order, continue_compensation_on_failure=source.continue_compensation_on_failure, data=context.kernel_data(declaration))


def _compile_step(context: CompilerContext, source: WorkflowStepDeclaration) -> WorkflowStep:
    return WorkflowStep(name=source.name, kind=WorkflowStepKind(source.kind), operation=context.semantic_id(source.operation) if source.operation else None, workflow=context.semantic_id(source.workflow) if source.workflow else None, compensation=_compile_compensation(context, source.compensation), nested_steps=tuple(_compile_step(context, item) for item in source.nested_steps), decision_cases=tuple(WorkflowDecisionCase(item.condition, item.target) for item in source.decision_cases), wait_event=context.semantic_id(source.wait_event) if source.wait_event else None, timeout_seconds=source.timeout_seconds)


def _compile_compensation(context: CompilerContext, source: CompensationDeclaration | None) -> Compensation | None:
    if source is None:
        return None
    return Compensation(context.semantic_id(source.operation), source.input_bindings, source.condition, source.retry_attempts, source.continue_on_failure)


__all__ = ["compile_workflow"]
