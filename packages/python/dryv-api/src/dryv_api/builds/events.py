from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from dryv.runtime import RuntimeEvent


class BuildEventType(StrEnum):
    ACCEPTED = "build.accepted"
    RESOURCES_READY = "build.resources_ready"
    RUNTIME = "build.runtime"
    PLAN_READY = "build.plan_ready"
    DIAGNOSTIC = "build.diagnostic"
    CANCELLED = "build.cancelled"
    FAILED = "build.failed"


@dataclass(frozen=True, slots=True)
class BuildEvent:
    sequence: int
    build_id: str
    type: BuildEventType
    message: str
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()
    runtime_stage: str | None = None


def runtime_build_event(sequence: int, event: RuntimeEvent) -> BuildEvent:
    return BuildEvent(
        sequence,
        event.build_id,
        BuildEventType.RUNTIME,
        event.message,
        event.subject,
        event.details,
        event.stage.value,
    )


__all__ = ["BuildEvent", "BuildEventType", "runtime_build_event"]
