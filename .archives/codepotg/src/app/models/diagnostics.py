"""Runtime diagnostic models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeDiagnostic:
    """A structured diagnostic emitted by runtime workflows."""

    level: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
