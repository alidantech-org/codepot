from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import SchemaRef


@dataclass(frozen=True, slots=True)
class FailureDeclaration:
    code: str
    schema: SchemaRef[object] | None = None
    message: str | None = None

    def __post_init__(self) -> None:
        if not self.code or self.code.strip() != self.code:
            raise ValueError("failure code must be a non-empty trimmed string")


__all__ = ["FailureDeclaration"]
