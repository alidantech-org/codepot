from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import PolicyRef, SchemaRef


@dataclass(frozen=True, slots=True)
class PolicyDeclaration:
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    ownership: str | None = None
    conditions: tuple[str, ...] = ()
    context_schema: SchemaRef[object] | None = None
    policies: tuple[PolicyRef, ...] = ()


__all__ = ["PolicyDeclaration"]
