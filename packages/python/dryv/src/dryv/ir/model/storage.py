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
        if not self.column.strip():
            raise ValueError("storage field mappings require a column name")
        if self.column_type is not None and not self.column_type.strip():
            raise ValueError("storage column_type must not be empty when provided")


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
        if not self.source.strip():
            raise ValueError("storage mappings require a source name")
        field_ids = tuple(item.field for item in self.fields)
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("storage mapped fields must be unique")
        columns = tuple(item.column for item in self.fields)
        if len(columns) != len(set(columns)):
            raise ValueError("storage mapped columns must be unique")
        if len(self.primary_key) != len(set(self.primary_key)):
            raise ValueError("storage primary-key fields must be unique")
        for index in self.indexes:
            if not index:
                raise ValueError("storage indexes must contain at least one field")
            if len(index) != len(set(index)):
                raise ValueError("fields within a storage index must be unique")
        if len(self.indexes) != len(set(self.indexes)):
            raise ValueError("storage indexes must be unique")


@dataclass(frozen=True, slots=True)
class StorageNamespace:
    mappings: tuple[StorageMapping, ...]
