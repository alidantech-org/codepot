"""Entity definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from archives.codepot.src.spec.ir.schema.entity.field.definition import EntityFieldDefinition
from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from pydantic import ConfigDict


class EntityDefinition(DefinitionItem):
    """Reusable entity schema definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    resource: Ref[Any] | None = None
    tags: list[str] | None = None
    extends: Ref[Any] | None = None
    abstract: bool | None = None
    fields: dict[str, EntityFieldDefinition]
