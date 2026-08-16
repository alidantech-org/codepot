from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import AuthorRef


def resolve_references(context: CompilerContext) -> None:
    for declaration in context.registry.all():
        for ref in _walk_refs(declaration.payload):
            try:
                context.declaration(ref)
            except ValueError as exc:
                context.error("AUTHOR_REF_INVALID", str(exc), declaration)


def _walk_refs(value: object) -> tuple[AuthorRef[Any], ...]:
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


__all__ = ["resolve_references"]
