from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering
from threading import Event
from typing import Generic, TypeVar
from uuid import uuid4

_VERSION_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


@total_ordering
@dataclass(frozen=True, slots=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("version components must be non-negative")
        for identifier in (*self.prerelease, *self.build):
            if not identifier or not re.fullmatch(r"[0-9A-Za-z-]+", identifier):
                raise ValueError(f"invalid semantic-version identifier: {identifier!r}")

    @classmethod
    def parse(cls, value: str) -> SemanticVersion:
        match = _VERSION_PATTERN.fullmatch(value.strip())
        if match is None:
            raise ValueError(f"invalid semantic version: {value!r}")
        prerelease = tuple(filter(None, (match.group("prerelease") or "").split(".")))
        build = tuple(filter(None, (match.group("build") or "").split(".")))
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=prerelease,
            build=build,
        )

    def __str__(self) -> str:
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value += "-" + ".".join(self.prerelease)
        if self.build:
            value += "+" + ".".join(self.build)
        return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return False
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        left = (self.major, self.minor, self.patch)
        right = (other.major, other.minor, other.patch)
        if left != right:
            return left < right
        return _compare_prerelease(self.prerelease, other.prerelease) < 0


def _compare_prerelease(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    if left == right:
        return 0
    if not left:
        return 1
    if not right:
        return -1
    for left_part, right_part in zip(left, right, strict=False):
        if left_part == right_part:
            continue
        left_numeric = left_part.isdigit()
        right_numeric = right_part.isdigit()
        if left_numeric and right_numeric:
            return -1 if int(left_part) < int(right_part) else 1
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return -1 if left_part < right_part else 1
    return -1 if len(left) < len(right) else 1


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


@dataclass(frozen=True, slots=True)
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
        if (self.end.line, self.end.column) < (self.start.line, self.start.column):
            raise ValueError("source span end must not precede start")
        if (
            self.start.offset is not None
            and self.end.offset is not None
            and self.end.offset < self.start.offset
        ):
            raise ValueError("source span end offset must not precede start offset")


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
        keys = tuple(key for key, _ in self.details)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("diagnostic details must have sorted unique keys")

    @property
    def is_error(self) -> bool:
        return self.severity is DiagnosticSeverity.ERROR

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
        return any(item.is_error for item in self.items)

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

    def to_dict(self) -> tuple[dict[str, object], ...]:
        return tuple(item.to_dict() for item in self.items)


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
        keys = tuple(key for key, _ in self.metadata)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("operation metadata must have sorted unique keys")
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
