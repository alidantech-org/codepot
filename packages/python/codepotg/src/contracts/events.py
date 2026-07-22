"""Shared progress event contracts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventLevel(str, Enum):
    """Supported runtime event levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass(frozen=True)
class RuntimeEvent:
    """Structured progress event emitted by app workflows or engines."""

    stage: str
    message: str
    level: EventLevel = EventLevel.INFO
    current: int | None = None
    total: int | None = None
    details: dict[str, Any] = field(default_factory=dict)


ProgressSink = Callable[[RuntimeEvent], None]
