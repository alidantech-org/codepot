"""Composite property definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from pydantic import ConfigDict

CompositePropertyRef = Ref[Any]


class CompositeDefinition(DefinitionItem):
    """Reusable composite property definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    extends: Ref[Any] | None = None
    properties: dict[str, CompositePropertyRef]
    resource: Ref[Any] | None = None
    entity: Ref[Any] | None = None
