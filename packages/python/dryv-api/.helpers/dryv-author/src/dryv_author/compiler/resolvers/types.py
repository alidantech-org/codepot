from dryv_author.compiler.context import CompilerContext
from dryv_author.core import RefKind
from dryv_author.features.schemas import SchemaDeclaration


def resolve_type_dependencies(context: CompilerContext) -> None:
    for declaration in context.declarations(RefKind.SCHEMA):
        source = context.normalized_payload(declaration, SchemaDeclaration)
        for field in source.fields:
            try:
                if field.annotation is not None:
                    context.type_expression(field.annotation)
                elif field.schema is not None:
                    context.type_expression(field.schema)
            except (TypeError, ValueError) as exc:
                context.error("AUTHOR_TYPE_INVALID", str(exc), declaration)


__all__ = ["resolve_type_dependencies"]
