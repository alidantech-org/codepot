"""Pipeline event contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PipelineEventLevel(StrEnum):
    """Pipeline event levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class PipelineEvent:
    """One progress/debug event emitted by the pipeline."""

    level: PipelineEventLevel
    pass_name: str
    message: str
    timestamp: datetime
    detail: str | None = None
