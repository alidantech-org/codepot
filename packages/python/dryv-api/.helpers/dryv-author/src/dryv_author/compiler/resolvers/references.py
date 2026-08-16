from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import AuthorRef, FieldRef, RefKind


def resolve_references(context: CompilerContext) -> None:
    for declaration in context.registry.all():
        for ref in walk_refs(declaration.payload):
            try:
                if isinstance(ref, FieldRef):
                    if ref.author_key != context.metadata.key:
                        raise ValueError("field reference belongs to another Author")
                    schema = context.registry.get(ref.schema_declaration_id)
                    if schema is None or schema.kind is not RefKind.SCHEMA:
                        raise ValueError(
                            f"field reference has unknown schema {ref.schema_declaration_id!r}"
                        )
                else:
                    context.declaration(ref)
            except ValueError as exc:
                context.error("AUTHOR_REF_INVALID", str(exc), declaration)


def walk_refs(value: object) -> tuple[AuthorRef[Any], ...]:
    result: list[AuthorRef[Any]] = []

    def visit(item: object) -> None:
        if isinstance(item, AuthorRef):
            result.append(item)
            return
        if is_dataclass(item) and not isinstance(item, type):
            for field in fields(item):
                visit(getattr(item, field.name))
            return
        if isinstance(item, (tuple, list)):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            for key, child in item.items():
                visit(key)
                visit(child)

    visit(value)
    return tuple(result)


__all__ = ["resolve_references", "walk_refs"]
