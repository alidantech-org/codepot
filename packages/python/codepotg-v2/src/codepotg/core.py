from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from threading import Event
from typing import Generic, TypeVar
from uuid import uuid4

_VERSION_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True, slots=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("version components must be non-negative")
        if any(not part for part in self.prerelease):
            raise ValueError("prerelease identifiers must not be empty")

    @classmethod
    def parse(cls, value: str) -> SemanticVersion:
        match = _VERSION_PATTERN.fullmatch(value.strip())
        if match is None:
            raise ValueError(f"invalid semantic version: {value!r}")
        prerelease = match.group("prerelease")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=tuple(prerelease.split(".")) if prerelease else (),
        )

    def _ordering_key(self) -> tuple[object, ...]:
        prerelease_key: tuple[tuple[int, object], ...] = tuple(
            (0, int(part)) if part.isdigit() else (1, part) for part in self.prerelease
        )
        return (
            self.major,
            self.minor,
            self.patch,
            1 if not self.prerelease else 0,
            prerelease_key,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._ordering_key() < other._ordering_key()

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return base if not self.prerelease else f"{base}-{'/'.join(self.prerelease)}".replace("/", ".")


@dataclass(frozen=True, slots=True)
class ApiVersion:
    value: str

    def __post_init__(self) -> None:
        if not self.value or self.value.strip() != self.value:
            raise ValueError("API version must be a non-empty trimmed string")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class BehaviorVersion:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValueError("behavior versions start at 1")

    def __str__(self) -> str:
        return str(self.value)


CORE_VERSION = SemanticVersion.parse("2.0.0-alpha.1")
PUBLIC_API_VERSION = ApiVersion("1")
PLUGIN_API_VERSION = ApiVersion("1")
IR_VERSION = SemanticVersion.parse("2.0.0-alpha.1")
NAMING_BEHAVIOR_VERSION = BehaviorVersion(1)
SELECTION_BEHAVIOR_VERSION = BehaviorVersion(1)
PLANNING_BEHAVIOR_VERSION = BehaviorVersion(1)


class SourceKind(str, Enum):
    FILE = "file"
    MEMORY = "memory"
    GIT = "git"
    GENERATED = "generated"
    PLUGIN = "plugin"


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    kind: SourceKind
    value: str

    def __post_init__(self) -> None:
        if not self.value:
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
            raise ValueError("source offsets must be non-negative")


@dataclass(frozen=True, slots=True)
class SourceSpan:
    source: SourceIdentity
    start: SourcePosition
    end: SourcePosition

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("source span end must not precede start")


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


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
        if not self.code or not self.message:
            raise ValueError("diagnostics require a code and message")
        if tuple(sorted(self.details, key=lambda item: item[0])) != self.details:
            raise ValueError("diagnostic details must be sorted by key")

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "span": _span_to_dict(self.span),
            "related": tuple(
                {"message": item.message, "span": _span_to_dict(item.span)}
                for item in self.related
            ),
            "details": dict(self.details),
            "suggestion": self.suggestion,
            "documentation": self.documentation,
        }


@dataclass(frozen=True, slots=True)
class Diagnostics:
    items: tuple[Diagnostic, ...] = ()

    @property
    def has_errors(self) -> bool:
        return any(item.severity is DiagnosticSeverity.ERROR for item in self.items)

    def add(self, *items: Diagnostic) -> Diagnostics:
        return Diagnostics(self.items + tuple(items))

    def extend(self, other: Diagnostics) -> Diagnostics:
        return Diagnostics(self.items + other.items)

    def sorted(self) -> Diagnostics:
        def key(item: Diagnostic) -> tuple[object, ...]:
            span = item.span
            return (
                span.source.kind.value if span else "",
                span.source.value if span else "",
                span.start.line if span else 0,
                span.start.column if span else 0,
                item.severity.value,
                item.code,
                item.message,
            )

        return Diagnostics(tuple(sorted(self.items, key=key)))


class OperationStatus(str, Enum):
    READY = "ready"
    GENERATED_WITH_WARNINGS = "generated_with_warnings"
    GENERATED_WITH_ACTIONS = "generated_with_actions"
    PARTIALLY_GENERATED = "partially_generated"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationCancelled(RuntimeError):
    pass


class CancellationToken:
    def __init__(self) -> None:
        self._event = Event()
        self._reason: str | None = None

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    @property
    def reason(self) -> str | None:
        return self._reason

    def cancel(self, reason: str = "cancelled") -> None:
        if not self._event.is_set():
            self._reason = reason
            self._event.set()

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise OperationCancelled(self._reason or "cancelled")


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class OperationResult(Generic[T]):
    status: OperationStatus
    data: T | None = None
    diagnostics: Diagnostics = field(default_factory=Diagnostics)
    operation_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        if tuple(sorted(self.metadata, key=lambda item: item[0])) != self.metadata:
            raise ValueError("operation metadata must be sorted by key")
        if self.status is OperationStatus.FAILED and not self.diagnostics.has_errors:
            raise ValueError("failed results require at least one error diagnostic")

    @property
    def ok(self) -> bool:
        return self.status not in {OperationStatus.FAILED, OperationStatus.CANCELLED}


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
