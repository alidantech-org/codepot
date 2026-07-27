from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import IntEnum


class AuthorDiagnosticSeverity(IntEnum):
    INFO = 10
    WARNING = 20
    ERROR = 30
    FATAL = 40


@dataclass(frozen=True, slots=True)
class AuthorDiagnostic:
    code: str
    message: str
    severity: AuthorDiagnosticSeverity = AuthorDiagnosticSeverity.ERROR
    declaration_path: str | None = None
    expected_kind: str | None = None
    actual_kind: str | None = None
    target: str | None = None
    details: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.code.startswith("AUTHOR_"):
            raise ValueError("author diagnostic codes must start with AUTHOR_")
        if not self.message or self.message.strip() != self.message:
            raise ValueError("diagnostic message must be a non-empty trimmed string")
        keys = tuple(key for key, _ in self.details)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("diagnostic details must be sorted by unique key")

    @property
    def is_error(self) -> bool:
        return self.severity >= AuthorDiagnosticSeverity.ERROR

    def sort_key(self) -> tuple[object, ...]:
        return (
            self.declaration_path or "",
            -int(self.severity),
            self.code,
            self.message,
            self.target or "",
        )


@dataclass(frozen=True, slots=True)
class AuthorDiagnostics:
    items: tuple[AuthorDiagnostic, ...] = ()

    @classmethod
    def from_iterable(cls, values: Iterable[AuthorDiagnostic]) -> AuthorDiagnostics:
        return cls(tuple(sorted(values, key=AuthorDiagnostic.sort_key)))

    def __iter__(self) -> Iterator[AuthorDiagnostic]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    @property
    def has_errors(self) -> bool:
        return any(item.is_error for item in self.items)

    def add(self, *values: AuthorDiagnostic) -> AuthorDiagnostics:
        return self.from_iterable((*self.items, *values))
