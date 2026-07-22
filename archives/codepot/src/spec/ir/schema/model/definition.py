"""Model definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref


class ModelArrayFieldDefinition(DefinitionItem):
    """Model field that represents an array of refs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["array"]
    items: Ref[Any]
    required: bool | None = None
    nullable: bool | None = None


ModelFieldDefinition = Ref[Any] | ModelArrayFieldDefinition


class ModelFieldSetsDefinition(DefinitionItem):
    """Optional field-set refs linked to a model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    select: Ref[Any] | None = None
    sort: Ref[Any] | None = None
    filter: Ref[Any] | None = None
    create: Ref[Any] | None = None
    update: Ref[Any] | None = None
    relations: Ref[Any] | None = None


class ModelDefinition(DefinitionItem):
    """Compiled model schema definition."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    from_: Ref[Any] = Field(alias="from")
    extends: Ref[Any] | None = None
    partial: bool | None = None
    field_sets: ModelFieldSetsDefinition | None = None
    fields: dict[str, ModelFieldDefinition]
