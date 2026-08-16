from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DiagnosticLevel(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class DiagnosticEntry:
    code: str
    message: str
    level: DiagnosticLevel = DiagnosticLevel.ERROR
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()


class DiagnosticsFeature:
    def from_error(self, error: Exception, *, subject: str | None = None) -> DiagnosticEntry:
        code = getattr(error, "code", type(error).__name__)
        message = getattr(error, "message", str(error))
        error_subject = getattr(error, "subject", None)
        return DiagnosticEntry(str(code), str(message), DiagnosticLevel.ERROR, error_subject or subject)


__all__ = ["DiagnosticEntry", "DiagnosticLevel", "DiagnosticsFeature"]
