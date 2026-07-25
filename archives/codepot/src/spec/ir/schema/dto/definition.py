"""DTO definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any, Literal

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from pydantic import ConfigDict, Field


class DtoArrayFieldDefinition(DefinitionItem):
    """DTO field that represents an array of refs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["array"]
    items: Ref[Any]
    required: bool | None = None
    nullable: bool | None = None


class DtoRefFieldDefinition(DefinitionItem):
    """DTO field that wraps a ref with local field options."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    ref: str = Field(alias="$ref")
    required: bool | None = None
    nullable: bool | None = None
    array: bool | None = None


DtoFieldDefinition = Ref[Any] | DtoRefFieldDefinition | DtoArrayFieldDefinition


class DtoDefinition(DefinitionItem):
    """Compiled DTO schema definition."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    from_: Ref[Any] | None = Field(default=None, alias="from")
    extends: Ref[Any] | None = None
    fields: dict[str, DtoFieldDefinition]
    partial: bool | None = None
