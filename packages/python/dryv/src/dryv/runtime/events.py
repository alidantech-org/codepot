from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


class RuntimeStage(StrEnum):
    STARTED = "started"
    PROJECT = "project"
    IR = "ir"
    PACKS = "packs"
    PLANNING = "planning"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    build_id: str
    stage: RuntimeStage
    message: str
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()


RuntimeEventSink = Callable[[RuntimeEvent], None]


__all__ = ["RuntimeEvent", "RuntimeEventSink", "RuntimeStage"]
