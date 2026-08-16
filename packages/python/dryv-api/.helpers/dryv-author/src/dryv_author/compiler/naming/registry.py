from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import declaration_id


@dataclass(frozen=True, slots=True)
class NameRegistry:
    owner_id: str

    def allocate(self, kind: str, name: str) -> str:
        return declaration_id(self.owner_id, kind, name)


__all__ = ["NameRegistry"]
