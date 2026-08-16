from __future__ import annotations

from dataclasses import dataclass

from dryv.ir import FrozenObject, FrozenValue

from dryv_author.core import FieldRef, SchemaRef, StorageRef


@dataclass(frozen=True, slots=True)
class StorageFieldDeclaration:
    field: FieldRef[object]
    column: str
    column_type: str | None = None
    indexed: bool = False
    unique: bool = False
    nullable: bool | None = None
    generated: bool = False
    computed: str | None = None
    default: FrozenValue = None


@dataclass(frozen=True, slots=True)
class StorageOnlyFieldDeclaration:
    name: str
    column: str
    column_type: str | None = None
    nullable: bool = False
    generated: bool = False
    computed: str | None = None
    default: FrozenValue = None


@dataclass(frozen=True, slots=True)
class StorageReferenceDeclaration:
    field: FieldRef[object]
    target_mapping: StorageRef[object]
    target_field: FieldRef[object]
    on_delete: str | None = None


@dataclass(frozen=True, slots=True)
class StorageDeclaration:
    schema: SchemaRef[object]
    source: str
    fields: tuple[StorageFieldDeclaration, ...] = ()
    primary_key: tuple[FieldRef[object], ...] = ()
    indexes: tuple[tuple[FieldRef[object], ...], ...] = ()
    storage_fields: tuple[StorageOnlyFieldDeclaration, ...] = ()
    omitted_fields: tuple[FieldRef[object], ...] = ()
    unique_constraints: tuple[tuple[str, tuple[str, ...]], ...] = ()
    storage_indexes: tuple[tuple[str, tuple[str, ...], bool], ...] = ()
    checks: tuple[tuple[str, str], ...] = ()
    references: tuple[StorageReferenceDeclaration, ...] = ()
    version_field: FieldRef[object] | None = None
    serialization: FrozenObject = ()


__all__ = ["StorageDeclaration", "StorageFieldDeclaration", "StorageOnlyFieldDeclaration", "StorageReferenceDeclaration"]
