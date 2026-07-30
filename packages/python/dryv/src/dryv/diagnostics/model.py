from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import IntEnum

from .source import SourceSpan


class DiagnosticSeverity(IntEnum):
    INFO = 10
    WARNING = 20
    ERROR = 30
    FATAL = 40


@dataclass(frozen=True, slots=True)
class RelatedLocation:
    message: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    severity: DiagnosticSeverity
    message: str
    span: SourceSpan | None = None
    related: tuple[RelatedLocation, ...] = ()
    details: tuple[tuple[str, object], ...] = ()
    suggestion: str | None = None
    documentation: str | None = None

    def __post_init__(self) -> None:
        if not self.code or self.code.strip() != self.code:
            raise ValueError("diagnostic code must be a non-empty trimmed string")
        if not self.message or self.message.strip() != self.message:
            raise ValueError("diagnostic message must be a non-empty trimmed string")
        keys = tuple(key for key, _ in self.details)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("diagnostic details must be sorted by unique key")

    @property
    def is_error(self) -> bool:
        return self.severity >= DiagnosticSeverity.ERROR

    def sort_key(self) -> tuple[object, ...]:
        if self.span is None:
            location: tuple[object, ...] = ("", "", 0, 0)
        else:
            location = (
                self.span.source.kind.value,
                self.span.source.value,
                self.span.start.line,
                self.span.start.column,
            )
        return (*location, -int(self.severity), self.code, self.message)

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity.name.lower(),
            "message": self.message,
            "span": _span_to_dict(self.span),
            "related": tuple(
                {"message": item.message, "span": _span_to_dict(item.span)} for item in self.related
            ),
            "details": dict(self.details),
            "suggestion": self.suggestion,
            "documentation": self.documentation,
        }


@dataclass(frozen=True, slots=True)
class Diagnostics:
    items: tuple[Diagnostic, ...] = ()

    @classmethod
    def from_iterable(cls, diagnostics: Iterable[Diagnostic]) -> Diagnostics:
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

    def add(self, *diagnostics: Diagnostic) -> Diagnostics:
        return self.from_iterable((*self.items, *diagnostics))

    def extend(self, diagnostics: Iterable[Diagnostic]) -> Diagnostics:
        return self.from_iterable((*self.items, *tuple(diagnostics)))

    def to_dict(self) -> tuple[dict[str, object], ...]:
        return tuple(item.to_dict() for item in self.items)


def _span_to_dict(span: SourceSpan | None) -> dict[str, object] | None:
    if span is None:
        return None
    return {
        "source": {"kind": span.source.kind.value, "value": span.source.value},
        "start": {
            "line": span.start.line,
            "column": span.start.column,
            "offset": span.start.offset,
        },
        "end": {
            "line": span.end.line,
            "column": span.end.column,
            "offset": span.end.offset,
        },
    }
