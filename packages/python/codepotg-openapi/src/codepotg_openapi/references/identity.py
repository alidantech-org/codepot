from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class ReferenceIdentity:
    document: str
    pointer: str

    @property
    def value(self) -> str:
        return f"{self.document}#{self.pointer}"
