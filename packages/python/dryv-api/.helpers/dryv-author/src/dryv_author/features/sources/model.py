from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import FieldRef, OperationRef, ValueSourceRef


@dataclass(frozen=True, slots=True)
class ValueSourceDependencyDeclaration:
    input: str
    source: ValueSourceRef[object]


@dataclass(frozen=True, slots=True)
class ValueSourceDeclaration:
    operation: OperationRef[object, object]
    output: str
    value_field: FieldRef[object]
    label_fields: tuple[FieldRef[object], ...]
    search_input: str | None = None
    dependencies: tuple[ValueSourceDependencyDeclaration, ...] = ()


__all__ = ["ValueSourceDeclaration", "ValueSourceDependencyDeclaration"]
