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


@dataclass(frozen=True, slots=True)
class EventEffect:
    event: SemanticId
    payload_schema: SemanticId | None = None
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class OperationEffects:
    events: tuple[EventEffect, ...] = ()
