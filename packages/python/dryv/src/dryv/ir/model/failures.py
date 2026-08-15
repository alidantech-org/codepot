from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class Failure:
    """Reusable semantic failure referenced by Operations and Workflows."""

    id: SemanticId
    name: Name
    code: str
    schema: SemanticId | None = None
    message: str | None = None
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("failure code must not be empty")
        if self.message is not None and not self.message.strip():
            raise ValueError("failure message must not be empty when provided")


__all__ = ["Failure"]
