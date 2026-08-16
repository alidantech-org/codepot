from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthorTarget:
    location: str
    attribute: str | None = None

    @classmethod
    def parse(cls, value: str) -> AuthorTarget:
        if not value or value.strip() != value:
            raise ValueError("author target must be a non-empty trimmed string")
        location, separator, attribute = value.rpartition(":")
        if separator and location and attribute.isidentifier():
            return cls(location, attribute)
        return cls(value)


__all__ = ["AuthorTarget"]
