from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class Policy:
    id: SemanticId
    name: Name
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    ownership: str | None = None
    conditions: tuple[str, ...] = ()
    data: KernelData = field(default_factory=KernelData)
