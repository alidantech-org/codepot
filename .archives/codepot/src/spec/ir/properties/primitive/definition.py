"""Primitive property definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.kinds.primitive import PrimitiveFormat, PrimitiveType
from pydantic import ConfigDict


class PrimitiveValidationDefinition(DefinitionItem):
    """Validation constraints for primitive properties."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None


class PrimitiveDefinition(DefinitionItem):
    """Reusable primitive property definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: PrimitiveType
    format: PrimitiveFormat | None = None
    validation: PrimitiveValidationDefinition | None = None
    example: Any | None = None
