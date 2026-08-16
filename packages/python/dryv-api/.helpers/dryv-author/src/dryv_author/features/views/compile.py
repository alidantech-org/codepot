from dryv.ir import Name, SemanticId, View, ViewConnection, ViewEventReaction, ViewTrigger, ViewWorkflowTrigger

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import ViewDeclaration


def compile_view(context: CompilerContext, declaration: Declaration) -> View:
    source = context.payload(declaration, ViewDeclaration)
    return View(id=SemanticId(declaration.id), name=Name(declaration.name), schema=context.semantic_id(source.schema) if source.schema else None, triggers=tuple(ViewTrigger(Name(item.name), context.semantic_id(item.operation), item.interaction, context.semantic_id(item.payload_schema) if item.payload_schema else None) for item in source.triggers), data=context.kernel_data(declaration), schemas=tuple(context.semantic_id(item) for item in source.schemas), fields=tuple(context.field_id(item) for item in source.fields), value_sources=tuple(context.semantic_id(item) for item in source.value_sources), workflow_triggers=tuple(ViewWorkflowTrigger(Name(item.name), context.semantic_id(item.workflow), item.interaction, context.semantic_id(item.payload_schema) if item.payload_schema else None) for item in source.workflow_triggers), event_reactions=tuple(ViewEventReaction(Name(item.name), context.semantic_id(item.event), item.reaction, context.semantic_id(item.payload_schema) if item.payload_schema else None) for item in source.event_reactions), connections=tuple(ViewConnection(Name(item.name), context.semantic_id(item.target)) for item in source.connections))


__all__ = ["compile_view"]
