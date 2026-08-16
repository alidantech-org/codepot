from __future__ import annotations

from dataclasses import dataclass

from dryv_author.refs import RefKind


@dataclass(frozen=True, slots=True)
class Declaration:
    id: str
    name: str
    kind: RefKind
    group_id: str | None = None
    payload: object | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("declaration id and name must not be empty")
