"""Enum property definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref

EnumValuePrimitive = str | int | float


class EnumValueDefinition(DefinitionItem):
    """Single enum value definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    value: EnumValuePrimitive
    label: str | None = None


class EnumDefinition(DefinitionItem):
    """Reusable enum property definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    values: list[EnumValueDefinition]
    resource: Ref[Any] | None = None
    entity: Ref[Any] | None = None
