from __future__ import annotations

from .declarations import Declaration
from .references import AuthorRef, RefKind


class DeclarationRegistry:
    def __init__(self, author_key: str) -> None:
        self.author_key = author_key
        self._items: dict[str, Declaration] = {}

    def register(self, declaration: Declaration) -> AuthorRef[object]:
        if declaration.id in self._items:
            current = self._items[declaration.id]
            raise ValueError(
                f"duplicate declaration id {declaration.id!r}: "
                f"{current.kind.value} {current.name!r} and {declaration.kind.value} {declaration.name!r}"
            )
        self._items[declaration.id] = declaration
        return declaration.ref(self.author_key)

    def require(self, ref: AuthorRef[object], expected: RefKind | None = None) -> Declaration:
        if ref.author_key != self.author_key:
            raise ValueError(f"reference {ref.declaration_id!r} belongs to another Author")
        try:
            declaration = self._items[ref.declaration_id]
        except KeyError as exc:
            raise ValueError(f"unknown declaration reference: {ref.declaration_id}") from exc
        if expected is not None and declaration.kind is not expected:
            raise ValueError(
                f"reference {ref.declaration_id!r} is {declaration.kind.value}, expected {expected.value}"
            )
        if ref.kind is not declaration.kind:
            raise ValueError(
                f"reference kind mismatch for {ref.declaration_id!r}: "
                f"{ref.kind.value} vs {declaration.kind.value}"
            )
        return declaration

    def get(self, declaration_id: str) -> Declaration | None:
        return self._items.get(declaration_id)

    def all(self) -> tuple[Declaration, ...]:
        return tuple(self._items[key] for key in sorted(self._items))

    def by_kind(self, kind: RefKind) -> tuple[Declaration, ...]:
        return tuple(item for item in self.all() if item.kind is kind)

    def by_owner(self, owner_id: str) -> tuple[Declaration, ...]:
        return tuple(item for item in self.all() if item.owner_id == owner_id)

    def __len__(self) -> int:
        return len(self._items)


__all__ = ["DeclarationRegistry"]
