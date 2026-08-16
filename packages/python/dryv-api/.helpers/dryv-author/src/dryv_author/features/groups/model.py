from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import GroupRef


@dataclass(frozen=True, slots=True)
class GroupDeclaration:
    parent: GroupRef | None = None
    path: tuple[str, ...] = ()


__all__ = ["GroupDeclaration"]
