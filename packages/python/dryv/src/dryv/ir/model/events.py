from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class Event:
    id: SemanticId
    name: Name
    payload_schema: SemanticId | None = None
    context_schema: SemanticId | None = None
    version: str | None = None
    source: str | None = None
    data: KernelData = field(default_factory=KernelData)
    policies: tuple[SemanticId, ...] = ()

    def __post_init__(self) -> None:
        if self.version is not None and not self.version.strip():
            raise ValueError("event version must not be empty when provided")
        if self.source is not None and not self.source.strip():
            raise ValueError("event source must not be empty when provided")
        if len(self.policies) != len(set(self.policies)):
            raise ValueError("event policy references must be unique")


@dataclass(frozen=True, slots=True)
class EventEffect:
    event: SemanticId
    payload_schema: SemanticId | None = None
    condition: str | None = None

    def __post_init__(self) -> None:
        if self.condition is not None and not self.condition.strip():
            raise ValueError("event effect condition must not be empty when provided")


@dataclass(frozen=True, slots=True)
class OperationEffects:
    events: tuple[EventEffect, ...] = ()

    def __post_init__(self) -> None:
        event_ids = tuple(item.event for item in self.events)
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("operation event effects must reference each event at most once")
