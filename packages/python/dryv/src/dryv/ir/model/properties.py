from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .field_behavior import FieldCapabilities
from .naming import Name
from .schemas import FieldConstraints
from .types import TypeExpression


@dataclass(frozen=True, slots=True)
class Property:
    """Reusable semantic property independent from any one Schema field."""

    id: SemanticId
    name: Name
    type: TypeExpression
    constraints: FieldConstraints = field(default_factory=FieldConstraints)
    capabilities: FieldCapabilities = field(default_factory=FieldCapabilities)
    data: KernelData = field(default_factory=KernelData)


__all__ = ["Property"]
