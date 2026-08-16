from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthorSource:
    source_id: str
    pointer: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or self.source_id.strip() != self.source_id:
            raise ValueError("source_id must be a non-empty trimmed string")
        if self.pointer is not None and not self.pointer.strip():
            raise ValueError("source pointer must not be empty")


__all__ = ["AuthorSource"]
