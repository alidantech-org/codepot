from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .base import FrozenObject, SemanticId, validate_frozen_object


@dataclass(frozen=True, slots=True)
class HttpFacet:
    method: str
    path: str
    operation_id: str | None = None

    def __post_init__(self) -> None:
        normalized = self.method.upper()
        if not normalized or not self.path.startswith("/"):
            raise ValueError("HTTP facets require a method and absolute route path")
        object.__setattr__(self, "method", normalized)


@dataclass(frozen=True, slots=True)
class AccessFacet:
    uses: tuple[SemanticId, ...] = ()
    inherited: tuple[SemanticId, ...] = ()
    effective: tuple[SemanticId, ...] = ()
    public: bool = False
    authenticated: bool = False

    def __post_init__(self) -> None:
        if self.public and self.authenticated:
            raise ValueError("access cannot be both public and authenticated")
        for label, values in (
            ("declared access policies", self.uses),
            ("inherited access policies", self.inherited),
            ("effective access policies", self.effective),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")


class TriggerKind(StrEnum):
    EVENT = "event"
    SCHEDULE = "schedule"
    HTTP = "http"
    INTERACTION = "interaction"
    STORAGE = "storage"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class TriggerFacet:
    kind: TriggerKind
    event: SemanticId | None = None
    expression: str | None = None
    method: str | None = None
    path: str | None = None
    view: SemanticId | None = None
    interaction: str | None = None
    storage: SemanticId | None = None
    signal: str | None = None

    def __post_init__(self) -> None:
        valid = {
            TriggerKind.EVENT: self.event is not None,
            TriggerKind.SCHEDULE: bool(self.expression),
            TriggerKind.HTTP: bool(self.method and self.path),
            TriggerKind.INTERACTION: self.view is not None and bool(self.interaction),
            TriggerKind.STORAGE: self.storage is not None,
            TriggerKind.SYSTEM: bool(self.signal),
        }
        if not valid[self.kind]:
            raise ValueError(f"trigger {self.kind.value} is missing required data")


class ExecutionPhase(StrEnum):
    BEFORE = "before"
    AROUND = "around"
    AFTER_SUCCESS = "after_success"
    AFTER_FAILURE = "after_failure"
    AFTER_COMPLETE = "after_complete"


@dataclass(frozen=True, slots=True)
class ExecutionHook:
    phase: ExecutionPhase
    operation: SemanticId
    order: int = 0
    condition: str | None = None
    can_stop: bool = False


@dataclass(frozen=True, slots=True)
class ExecutionFacet:
    hooks: tuple[ExecutionHook, ...] = ()


@dataclass(frozen=True, slots=True)
class EventsFacet:
    consumes: tuple[SemanticId, ...] = ()
    channels: tuple[str, ...] = ()
    bindings: FrozenObject = ()

    def __post_init__(self) -> None:
        if len(self.consumes) != len(set(self.consumes)):
            raise ValueError("consumed events must be unique")
        validate_frozen_object("event bindings", self.bindings)


@dataclass(frozen=True, slots=True)
class OperationFacets:
    http: HttpFacet | None = None
    access: AccessFacet | None = None
    trigger: TriggerFacet | None = None
    execution: ExecutionFacet | None = None
    events: EventsFacet | None = None


@dataclass(frozen=True, slots=True)
class WorkflowFacets:
    trigger: TriggerFacet | None = None
    access: AccessFacet | None = None
    execution: ExecutionFacet | None = None
    events: EventsFacet | None = None
    durable: bool = False
    timeout_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.timeout_seconds is not None and self.timeout_seconds < 1:
            raise ValueError("workflow timeout must be positive")


@dataclass(frozen=True, slots=True)
class GroupFacets:
    access: AccessFacet | None = None
    execution: ExecutionFacet | None = None
