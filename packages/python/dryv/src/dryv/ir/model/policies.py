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

    def __post_init__(self) -> None:
        for label, values in (("roles", self.roles), ("permissions", self.permissions), ("scopes", self.scopes), ("conditions", self.conditions)):
            if any(not value.strip() for value in values):
                raise ValueError(f"policy {label} must not contain empty values")
            if len(values) != len(set(values)):
                raise ValueError(f"policy {label} must be unique")
        if self.ownership is not None and not self.ownership.strip():
            raise ValueError("policy ownership must not be empty when provided")
