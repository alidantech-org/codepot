from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import PolicyRef, SchemaRef


@dataclass(frozen=True, slots=True)
class EventDeclaration:
    payload_schema: SchemaRef[object] | None = None
    context_schema: SchemaRef[object] | None = None
    version: str | None = None
    source: str | None = None
    policies: tuple[PolicyRef, ...] = ()


__all__ = ["EventDeclaration"]
