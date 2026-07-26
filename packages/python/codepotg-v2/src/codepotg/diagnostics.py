from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, Iterator


class DiagnosticSeverity(IntEnum):
    INFO = 10
    WARNING = 20
    ERROR = 30
    FATAL = 40


@dataclass(frozen=True, slots=True, order=True)
class SourceIdentity:
    """Stable identity for a file, memory input, pack snapshot, or generated artifact."""

    kind: str
    value: str

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("source identity kind must not be empty")
        if not self.value.strip():
            raise ValueError("source identity value must not be empty")


@dataclass(frozen=True, slots=True, order=True)
class SourcePosition:
    line: int
    column: int
    offset: int | None = None

    def __post_init__(self) -> None:
        if self.line < 1 or self.column < 1:
            raise ValueError("source positions are one-based")
        if self.offset is not None and self.offset < 0:
            raise ValueError("source offset must be non-negative")


@dataclass(frozen=True, slots=True, order=True)
class SourceSpan:
    source: SourceIdentity
    start: SourcePosition
    end: SourcePosition

    def __post_init__(self) -> None:
        if (self.end.line, self.end.column) < (self.start.line, self.start.column):
            raise ValueError("source span end must not precede start")
        if (
            self.start.offset is not None
            and self.end.offset is not None
            and self.end.offset < self.start.offset
        ):
            raise ValueError("source span end offset must not precede start offset")


@dataclass(frozen=True, slots=True, order=True)
class DiagnosticCode:
    namespace: str
    number: int

    def __post_init__(self) -> None:
        normalized = self.namespace.strip().upper()
        if not normalized or not normalized.replace("_", "").isalnum():
            raise ValueError("diagnostic namespace must be alphanumeric")
        if self.number < 1:
            raise ValueError("diagnostic number must be positive")
        object.__setattr__(self, "namespace", normalized)

    def __str__(self) -> str:
        return f"{self.namespace}{self.number:04d}"


@dataclass(frozen=True, slots=True)
class RelatedLocation:
    message: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    span: SourceSpan | None = None
    related: tuple[RelatedLocation, ...] = ()
    details: tuple[tuple[str, str], ...] = ()
    suggestion: str | None = None
    documentation: str | None = None

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("diagnostic message must not be empty")
        keys = tuple(key for key, _ in self.details)
        if len(keys) != len(set(keys)):
            raise ValueError("diagnostic detail keys must be unique")
        if any(not key.strip() for key in keys):
            raise ValueError("diagnostic detail keys must not be empty")

    @property
    def is_error(self) -> bool:
        return self.severity >= DiagnosticSeverity.ERROR

    def sort_key(self) -> tuple[object, ...]:
        if self.span is None:
            location: tuple[object, ...] = ("", "", 0, 0)
        else:
            location = (
                self.span.source.kind,
                self.span.source.value,
                self.span.start.line,
                self.span.start.column,
            )
        return (*location, -int(self.severity), str(self.code), self.message)


@dataclass(frozen=True, slots=True)
class DiagnosticCollection:
    items: tuple[Diagnostic, ...] = ()

    @classmethod
    def from_iterable(cls, diagnostics: Iterable[Diagnostic]) -> DiagnosticCollection:
        return cls(tuple(sorted(diagnostics, key=Diagnostic.sort_key)))

    def __iter__(self) -> Iterator[Diagnostic]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)

    @property
    def has_errors(self) -> bool:
        return any(item.is_error for item in self.items)

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(item for item in self.items if item.is_error)

    def add(self, diagnostic: Diagnostic) -> DiagnosticCollection:
        return self.from_iterable((*self.items, diagnostic))

    def extend(self, diagnostics: Iterable[Diagnostic]) -> DiagnosticCollection:
        return self.from_iterable((*self.items, *tuple(diagnostics)))
