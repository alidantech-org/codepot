from __future__ import annotations

from dryv.ir import FieldConstraints, Name, Property, SemanticId

from dryv_author.core import Declaration
from dryv_author.compiler.context import CompilerContext

from .model import PropertyDeclaration


def compile_property(context: CompilerContext, declaration: Declaration) -> Property:
    source = context.payload(declaration, PropertyDeclaration)
    return Property(
        SemanticId(declaration.id),
        Name(declaration.name),
        context.type_expression(source.annotation),
        constraints=FieldConstraints(
            minimum=source.options.minimum,
            maximum=source.options.maximum,
            min_length=source.options.min_length,
            max_length=source.options.max_length,
            pattern=source.options.pattern,
            format=source.options.format,
        ),
        capabilities=source.capabilities,
        data=context.kernel_data(declaration),
    )


__all__ = ["compile_property"]
