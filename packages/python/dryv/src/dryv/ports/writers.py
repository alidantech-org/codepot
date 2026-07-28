from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol, runtime_checkable

from dryv.generation.models import MemoryOutput

_STATE_PATH = ".dryv/generation-state.json"


class ManagedWriteKind(StrEnum):
    CREATE = "create"
    CHANGE = "change"
    DELETE = "delete"
    LEAVE = "leave"
    PROTECT = "protect"


@dataclass(frozen=True, slots=True)
class ManagedWriteChange:
    path: str
    kind: ManagedWriteKind
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ManagedWriteReport:
    changes: tuple[ManagedWriteChange, ...]
    state_path: str = _STATE_PATH

    @property
    def changed(self) -> bool:
        return any(
            item.kind
            in {
                ManagedWriteKind.CREATE,
                ManagedWriteKind.CHANGE,
                ManagedWriteKind.DELETE,
            }
            for item in self.changes
        )


@runtime_checkable
class ManagedOutputWriter(Protocol):
    def write(self, output: MemoryOutput, root: str | Path) -> ManagedWriteReport: ...
