from __future__ import annotations

from dataclasses import dataclass

from .references import AuthorRef, RefKind, make_ref
from .source import AuthorSource


@dataclass(frozen=True, slots=True)
class Declaration:
    id: str
    name: str
    kind: RefKind
    owner_id: str
    payload: object
    source: AuthorSource | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.name or not self.owner_id:
            raise ValueError("declarations require id, name and owner_id")

    def ref(self, author_key: str) -> AuthorRef[object]:
        return make_ref(author_key, self.id, self.kind)


__all__ = ["Declaration"]
