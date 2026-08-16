from __future__ import annotations

from dataclasses import replace

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import RefKind

from .model import SchemaDeclaration
from .projection import apply_projections


def resolve_schemas(context: CompilerContext) -> None:
    by_id = {item.id: context.payload(item, SchemaDeclaration) for item in context.declarations(RefKind.SCHEMA)}
    resolved: dict[str, SchemaDeclaration] = {}
    visiting: set[str] = set()
    def resolve(identifier: str) -> SchemaDeclaration:
        if identifier in resolved:
            return resolved[identifier]
        if identifier in visiting:
            raise ValueError(f"schema projection cycle includes {identifier!r}")
        visiting.add(identifier)
        source = by_id[identifier]
        if source.source is not None:
            source_declaration = context.declaration(source.source)
            base = resolve(source_declaration.id)
            source = replace(source, fields=apply_projections(base.fields, source.projections), source=None, projections=())
        visiting.remove(identifier)
        resolved[identifier] = source
        return source
    for identifier in sorted(by_id):
        context.set_normalized(identifier, resolve(identifier))


__all__ = ["resolve_schemas"]
