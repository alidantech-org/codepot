"""Entity field definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from archives.codepot.src.spec.kinds.fields import (
    EntityRelationKind,
    FieldPersistenceMode,
    FieldVisibilityLevel,
    QueryOperator,
)
from pydantic import ConfigDict, Field


class FieldCapabilityConfig(DefinitionItem):
    """Field query/sort/select capability configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    filter: bool | None = None
    sort: bool | None = None
    select: bool | None = None
    operators: list[QueryOperator] | None = None


class FieldVisibilityConfig(DefinitionItem):
    """Field read/write visibility configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    read: FieldVisibilityLevel | None = None
    write: FieldVisibilityLevel | None = None
    sensitive: bool | None = None


class FieldLifecycleConfig(DefinitionItem):
    """Field lifecycle configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    create: bool | None = None
    update: bool | None = None
    immutable: bool | None = None
    generated: bool | None = None
    read_only: bool | None = None


class FieldPersistenceConfig(DefinitionItem):
    """Field persistence configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: FieldPersistenceMode
    generated: bool | None = None
    immutable: bool | None = None


class ArrayDefinition(DefinitionItem):
    """Array field constraints."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None


class EntityRelationThroughDefinition(DefinitionItem):
    """Join-through relation definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entity: Ref[Any]
    from_: Ref[Any] = Field(alias="from")
    to: Ref[Any]


class EntityRelationDefinition(DefinitionItem):
    """Entity relation target configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    relation: EntityRelationKind
    target: Ref[Any]
    inverse: Ref[Any] | None = None
    through: EntityRelationThroughDefinition | None = None


class EntityFieldOptionsDefinition(DefinitionItem):
    """Common options shared by property and relation fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    required: bool | None = None
    nullable: bool | None = None
    array: bool | ArrayDefinition | None = None
    default: Any | None = None

    capability: FieldCapabilityConfig | None = None
    visibility: FieldVisibilityConfig | None = None
    lifecycle: FieldLifecycleConfig | None = None
    persistence: FieldPersistenceConfig | None = None


class EntityPropertyFieldDefinition(EntityFieldOptionsDefinition):
    """Entity field backed by a reusable property ref."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    ref: str = Field(alias="$ref")


class EntityRelationFieldDefinition(EntityRelationDefinition, EntityFieldOptionsDefinition):
    """Entity field backed by a relation target."""

    model_config = ConfigDict(frozen=True, extra="forbid")


EntityFieldDefinition = EntityPropertyFieldDefinition | EntityRelationFieldDefinition
