from dryv_author.compiler.context import CompilerContext
from dryv_author.compiler.resolvers import (
    resolve_field_references,
    resolve_references,
    resolve_type_dependencies,
)
from dryv_author.features.schemas import resolve_schemas


def resolve(context: CompilerContext) -> None:
    resolve_references(context)
    if context.diagnostics.has_errors:
        return
    resolve_schemas(context)
    resolve_field_references(context)
    resolve_type_dependencies(context)


__all__ = ["resolve"]
