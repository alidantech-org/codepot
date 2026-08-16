from __future__ import annotations

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import FieldRef

from .references import walk_refs


def resolve_field_references(context: CompilerContext) -> None:
    for declaration in context.registry.all():
        for ref in walk_refs(declaration.payload):
            if not isinstance(ref, FieldRef):
                continue
            try:
                context.field_id(ref)
            except ValueError as exc:
                context.error("AUTHOR_FIELD_REF_INVALID", str(exc), declaration)


__all__ = ["resolve_field_references"]
