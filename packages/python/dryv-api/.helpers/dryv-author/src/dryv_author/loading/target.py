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
        if ":" in value:
            location, attribute = value.rsplit(":", 1)
            if not location or not attribute:
                raise ValueError("author target must use location[:attribute]")
            return cls(location, attribute)
        return cls(value)


__all__ = ["AuthorTarget"]
