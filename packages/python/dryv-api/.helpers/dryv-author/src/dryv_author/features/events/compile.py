from dryv.ir import Event, Name, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import EventDeclaration


def compile_event(context: CompilerContext, declaration: Declaration) -> Event:
    source = context.payload(declaration, EventDeclaration)
    return Event(SemanticId(declaration.id), Name(declaration.name), context.semantic_id(source.payload_schema) if source.payload_schema else None, context.semantic_id(source.context_schema) if source.context_schema else None, source.version, source.source, context.kernel_data(declaration), tuple(context.semantic_id(item) for item in source.policies))


__all__ = ["compile_event"]
