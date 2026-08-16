from __future__ import annotations

from dryv_author.compiler.context import CompilerContext


def validate_declarations(context: CompilerContext) -> None:
    for declaration in context.registry.all():
        if declaration.owner_id != declaration.id and context.registry.get(declaration.owner_id) is None:
            context.error("AUTHOR_OWNER_UNKNOWN", f"declaration {declaration.id!r} has unknown owner {declaration.owner_id!r}", declaration)


__all__ = ["validate_declarations"]
