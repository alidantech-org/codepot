from __future__ import annotations

from dataclasses import dataclass

from .naming import author_key
from .source import AuthorSource


@dataclass(frozen=True, slots=True)
class AuthorMetadata:
    name: str
    version: str | None = None
    source: AuthorSource | None = None

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("author name must be a non-empty trimmed string")
        if self.version is not None and not self.version.strip():
            raise ValueError("author version must not be empty when provided")

    @property
    def key(self) -> str:
        return author_key(self.name, None if self.source is None else self.source.source_id)


__all__ = ["AuthorMetadata"]
