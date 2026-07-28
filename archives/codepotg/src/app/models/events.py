"""Runtime progress event models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    """A structured runtime progress event."""

    stage: str
    message: str
    level: str = "info"
    current: int | None = None
    total: int | None = None
    details: dict[str, Any] = field(default_factory=dict)


ProgressSink = Callable[[RuntimeEvent], None]
