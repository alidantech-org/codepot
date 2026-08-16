from __future__ import annotations

from dryv.ir import EventEffect, HttpFacet, Name, Operation, OperationEffects, OperationFacets, OperationOutput, OperationRelations, SchemaUse, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import OperationDeclaration


def compile_operation(context: CompilerContext, declaration: Declaration) -> Operation:
    source = context.payload(declaration, OperationDeclaration)
    http = HttpFacet(source.http_method, source.http_path, source.operation_id) if source.http_method is not None and source.http_path is not None else None
    return Operation(id=SemanticId(declaration.id), name=Name(declaration.name), inputs=tuple(SchemaUse(Name(item.name), context.semantic_id(item.schema), item.required, item.nullable, item.readonly) for item in source.inputs), outputs=tuple(OperationOutput(Name(item.name) if item.name else None, context.semantic_id(item.schema) if item.schema else None, item.optional) for item in source.outputs), failures=tuple(context.semantic_id(item) for item in source.failures), effects=OperationEffects(tuple(EventEffect(context.semantic_id(item.event), context.semantic_id(item.payload_schema) if item.payload_schema else None, item.condition) for item in source.events)), facets=OperationFacets(http=http), data=context.kernel_data(declaration), subjects=tuple(context.semantic_id(item) for item in source.subjects), policies=tuple(context.semantic_id(item) for item in source.policies), relations=OperationRelations(invokes=tuple(context.semantic_id(item) for item in source.relations.invokes), requires=tuple(context.semantic_id(item) for item in source.relations.requires), delegates_to=tuple(context.semantic_id(item) for item in source.relations.delegates_to), before=tuple(context.semantic_id(item) for item in source.relations.before), after=tuple(context.semantic_id(item) for item in source.relations.after), triggers_workflows=tuple(context.semantic_id(item) for item in source.relations.triggers_workflows)))


__all__ = ["compile_operation"]
