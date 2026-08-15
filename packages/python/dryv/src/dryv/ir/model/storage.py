from __future__ import annotations

from dataclasses import dataclass, field

from .base import FrozenObject, FrozenValue, KernelData, SemanticId, validate_frozen_object
from .naming import Name


@dataclass(frozen=True, slots=True)
class StorageFieldMapping:
    field: SemanticId
    column: str
    column_type: str | None = None
    indexed: bool = False
    unique: bool = False
    nullable: bool | None = None
    generated: bool = False
    computed: str | None = None
    default: FrozenValue = None

    def __post_init__(self) -> None:
        if not self.column.strip():
            raise ValueError("storage field mappings require a column name")
        if self.column_type is not None and not self.column_type.strip():
            raise ValueError("storage column_type must not be empty when provided")
        if self.computed is not None and not self.computed.strip():
            raise ValueError("storage computed expression must not be empty when provided")
        if self.computed is not None and not self.generated:
            raise ValueError("computed storage fields must be marked generated")


@dataclass(frozen=True, slots=True)
class StorageOnlyField:
    """Persistence-only field that does not become Schema meaning."""

    name: str
    column: str
    column_type: str | None = None
    nullable: bool = False
    generated: bool = False
    computed: str | None = None
    default: FrozenValue = None

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("storage-only fields require a non-empty trimmed name")
        if not self.column or self.column.strip() != self.column:
            raise ValueError("storage-only fields require a non-empty trimmed column")
        if self.column_type is not None and not self.column_type.strip():
            raise ValueError("storage-only column_type must not be empty when provided")
        if self.computed is not None and not self.computed.strip():
            raise ValueError("storage-only computed expression must not be empty")
        if self.computed is not None and not self.generated:
            raise ValueError("computed storage-only fields must be generated")


@dataclass(frozen=True, slots=True)
class StorageUniqueConstraint:
    name: str
    columns: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_named_columns("storage unique constraint", self.name, self.columns)


@dataclass(frozen=True, slots=True)
class StorageIndex:
    name: str
    columns: tuple[str, ...]
    unique: bool = False

    def __post_init__(self) -> None:
        _validate_named_columns("storage index", self.name, self.columns)


@dataclass(frozen=True, slots=True)
class StorageCheck:
    name: str
    expression: str

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("storage checks require a non-empty trimmed name")
        if not self.expression or self.expression.strip() != self.expression:
            raise ValueError("storage checks require a non-empty trimmed expression")


@dataclass(frozen=True, slots=True)
class StorageReferenceMapping:
    field: SemanticId
    target_mapping: SemanticId
    target_field: SemanticId
    on_delete: str | None = None

    def __post_init__(self) -> None:
        if self.on_delete is not None and not self.on_delete.strip():
            raise ValueError("storage reference on_delete must not be empty when provided")


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
    storage_fields: tuple[StorageOnlyField, ...] = ()
    omitted_fields: tuple[SemanticId, ...] = ()
    unique_constraints: tuple[StorageUniqueConstraint, ...] = ()
    storage_indexes: tuple[StorageIndex, ...] = ()
    checks: tuple[StorageCheck, ...] = ()
    references: tuple[StorageReferenceMapping, ...] = ()
    version_field: SemanticId | None = None
    serialization: FrozenObject = ()

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("storage mappings require a source name")
        field_ids = tuple(item.field for item in self.fields)
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("storage mapped fields must be unique")
        storage_names = tuple(item.name for item in self.storage_fields)
        if len(storage_names) != len(set(storage_names)):
            raise ValueError("storage-only field names must be unique")
        columns = tuple(item.column for item in self.fields) + tuple(item.column for item in self.storage_fields)
        if len(columns) != len(set(columns)):
            raise ValueError("storage columns must be unique across mapped and storage-only fields")
        if len(self.primary_key) != len(set(self.primary_key)):
            raise ValueError("storage primary-key fields must be unique")
        if len(self.omitted_fields) != len(set(self.omitted_fields)):
            raise ValueError("omitted semantic fields must be unique")
        if set(field_ids) & set(self.omitted_fields):
            raise ValueError("a semantic field cannot be both mapped and omitted")
        for index in self.indexes:
            if not index:
                raise ValueError("storage indexes must contain at least one field")
            if len(index) != len(set(index)):
                raise ValueError("fields within a storage index must be unique")
        if len(self.indexes) != len(set(self.indexes)):
            raise ValueError("storage indexes must be unique")
        for label, items in (
            ("unique constraint names", self.unique_constraints),
            ("storage index names", self.storage_indexes),
            ("storage check names", self.checks),
        ):
            names = tuple(item.name for item in items)
            if len(names) != len(set(names)):
                raise ValueError(f"{label} must be unique")
        reference_fields = tuple(item.field for item in self.references)
        if len(reference_fields) != len(set(reference_fields)):
            raise ValueError("storage reference mappings must have unique local fields")
        validate_frozen_object("storage serialization", self.serialization)


@dataclass(frozen=True, slots=True)
class StorageNamespace:
    mappings: tuple[StorageMapping, ...]


def _validate_named_columns(label: str, name: str, columns: tuple[str, ...]) -> None:
    if not name or name.strip() != name:
        raise ValueError(f"{label} requires a non-empty trimmed name")
    if not columns:
        raise ValueError(f"{label} requires at least one column")
    if any(not column or column.strip() != column for column in columns):
        raise ValueError(f"{label} columns must be non-empty trimmed strings")
    if len(columns) != len(set(columns)):
        raise ValueError(f"{label} columns must be unique")
