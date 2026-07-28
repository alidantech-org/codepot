from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SourceKind(StrEnum):
    FILE = "file"
    MEMORY = "memory"
    GIT = "git"
    SEMANTIC = "semantic"
    TEMPLATE = "template"
    PLANNED_ARTIFACT = "planned_artifact"
    GENERATED_ARTIFACT = "generated_artifact"
    PLUGIN = "plugin"


@dataclass(frozen=True, slots=True, order=True)
class SourceIdentity:
    kind: SourceKind
    value: str

    def __post_init__(self) -> None:
        if not self.value or self.value.strip() != self.value:
            raise ValueError("source identity value must be a non-empty trimmed string")


@dataclass(frozen=True, slots=True, order=True)
class SourcePosition:
    line: int
    column: int
    offset: int | None = None

    def __post_init__(self) -> None:
        if self.line < 1 or self.column < 1:
            raise ValueError("source positions are one-based")
        if self.offset is not None and self.offset < 0:
            raise ValueError("source offsets must be non-negative")


@dataclass(frozen=True, slots=True, order=True)
class SourceSpan:
    source: SourceIdentity
    start: SourcePosition
    end: SourcePosition

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("source span end must not precede start")
