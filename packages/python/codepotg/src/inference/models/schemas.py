"""Schema inference model types."""

from dataclasses import dataclass, field
from typing import Any

from inference.models.base import InferredSchemaKind
from inference.models.resources import InferredResource


@dataclass(frozen=True)
class QueryMetadata:
    """Query metadata from x-codegen.query."""

    filterable: bool = False
    operators: tuple[str, ...] = field(default_factory=tuple)
    sortable: bool = False
    selectable: bool = False
    searchable: bool = False

    @property
    def enabled(self) -> bool:
        """Return whether any query behavior is enabled."""
        return bool(
            self.filterable
            or self.operators
            or self.sortable
            or self.selectable
            or self.searchable
        )


@dataclass(frozen=True)
class InferredSchemaField:
    """Inferred field from an OpenAPI schema object."""

    name: str
    required: bool
    nullable: bool
    raw_type: str | None = None
    format: str | None = None
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = field(default_factory=tuple)
    item_ref: str | None = None
    item_refs: tuple[str, ...] = field(default_factory=tuple)
    enum_values: tuple[str, ...] | None = None
    default: Any = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    exclusive_minimum: bool | int | float | None = None
    exclusive_maximum: bool | int | float | None = None
    multiple_of: int | float | None = None
    pattern: str | None = None
    description: str | None = None
    # Resolved type information for emitters
    resolved_kind: str | None = None
    resolved_type: str | None = None
    resolved_format: str | None = None
    resolved_item_kind: str | None = None
    resolved_item_type: str | None = None
    resolved_item_format: str | None = None
    # Query metadata from x-codegen.query
    query: QueryMetadata = field(default_factory=QueryMetadata)


@dataclass(frozen=True)
class InferredSchemaComposition:
    """Inferred composition from OpenAPI schema allOf/anyOf/oneOf."""

    kind: str
    refs: tuple[str, ...] = field(default_factory=tuple)
    inline_field_count: int = 0


@dataclass(frozen=True)
class InferredSchema:
    """Inferred schema from OpenAPI components."""

    name: str
    ref: str
    kind: "InferredSchemaKind"
    resource: "InferredResource | None" = None
    x_codegen: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    alias_of: str | None = None
    is_alias: bool = False
    nullable: bool = False
    # Primitive fields
    primitive_type: str | None = None
    primitive_format: str | None = None
    query: QueryMetadata = field(default_factory=QueryMetadata)
    # Enum fields
    enum_type: str | None = None
    enum_values: tuple[str, ...] = field(default_factory=tuple)
    # Model/dto fields
    fields: tuple[InferredSchemaField, ...] = field(default_factory=tuple)
    composition_refs: tuple[str, ...] = field(default_factory=tuple)
    inherited_refs: tuple[str, ...] = field(default_factory=tuple)
    composition: InferredSchemaComposition | None = None
