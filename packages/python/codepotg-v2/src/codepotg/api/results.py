from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import uuid4

from codepotg.diagnostics import Diagnostics


class OperationStatus(StrEnum):
    READY = "ready"
    GENERATED_WITH_WARNINGS = "generated_with_warnings"
    GENERATED_WITH_ACTIONS = "generated_with_actions"
    PARTIALLY_GENERATED = "partially_generated"
    FAILED = "failed"
    CANCELLED = "cancelled"


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class OperationResult(Generic[T]):
    status: OperationStatus
    data: T | None = None
    diagnostics: Diagnostics = field(default_factory=Diagnostics)
    operation_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        keys = tuple(key for key, _ in self.metadata)
        if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
            raise ValueError("operation metadata must be sorted by unique key")
        if self.status is OperationStatus.FAILED and not self.diagnostics.has_errors:
            raise ValueError("failed results require at least one error diagnostic")

    @property
    def ok(self) -> bool:
        return self.status not in {OperationStatus.FAILED, OperationStatus.CANCELLED}
