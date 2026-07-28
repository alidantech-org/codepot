from __future__ import annotations

from dataclasses import dataclass, field

from .base import KernelData, SemanticId
from .naming import Name


@dataclass(frozen=True, slots=True)
class StorageFieldMapping:
    field: SemanticId
    column: str
    column_type: str | None = None
    indexed: bool = False
    unique: bool = False
    nullable: bool | None = None

    def __post_init__(self) -> None:
        if not self.column:
            raise ValueError("storage field mappings require a column name")


@dataclass(frozen=True, slots=True)
class StorageMapping:
    id: SemanticId
    name: Name
    schema: SemanticId
    source: str
    fields: tuple[StorageFieldMapping, ...] = ()
    primary_key: tuple[SemanticId, ...] = ()
    indexes: tuple[tuple[SemanticId, ...], ...] = ()
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("storage mappings require a source name")
        field_ids = tuple(item.field for item in self.fields)
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("storage mapped fields must be unique")
        if len(self.primary_key) != len(set(self.primary_key)):
            raise ValueError("storage primary-key fields must be unique")


@dataclass(frozen=True, slots=True)
class StorageNamespace:
    mappings: tuple[StorageMapping, ...]
