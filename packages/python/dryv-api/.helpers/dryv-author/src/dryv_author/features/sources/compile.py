from dryv.ir import Name, SemanticId, ValueSource, ValueSourceDependency

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import ValueSourceDeclaration


def compile_value_source(context: CompilerContext, declaration: Declaration) -> ValueSource:
    source = context.payload(declaration, ValueSourceDeclaration)
    return ValueSource(SemanticId(declaration.id), Name(declaration.name), context.semantic_id(source.operation), source.output, context.field_id(source.value_field), tuple(context.field_id(item) for item in source.label_fields), source.search_input, context.kernel_data(declaration), tuple(ValueSourceDependency(item.input, context.semantic_id(item.source)) for item in source.dependencies))


__all__ = ["compile_value_source"]
