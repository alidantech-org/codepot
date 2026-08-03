"""Pipeline diagnostic contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PipelineDiagnosticLevel(StrEnum):
    """Diagnostic severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class PipelineDiagnostic:
    """One pipeline diagnostic message."""

    level: PipelineDiagnosticLevel
    message: str
    pass_name: str
    code: str | None = None
    detail: str | None = None
