from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .base import SemanticId


class FieldWriteMode(StrEnum):
    CALLER = "caller"
    SYSTEM = "system"
    DERIVED = "derived"
    FORBIDDEN = "forbidden"


class FieldVisibility(StrEnum):
    EXPOSED = "exposed"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"


class QueryOperator(StrEnum):
    EQ = "eq"
    NE = "ne"
    IN = "in"
    NOT_IN = "not_in"
    PREFIX = "prefix"
    CONTAINS = "contains"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    BETWEEN = "between"


@dataclass(frozen=True, slots=True)
class FieldLifecycle:
    initialize: FieldWriteMode = FieldWriteMode.CALLER
    mutate: FieldWriteMode = FieldWriteMode.CALLER
    visibility: FieldVisibility = FieldVisibility.EXPOSED


@dataclass(frozen=True, slots=True)
class FieldQuery:
    operators: tuple[QueryOperator, ...] = ()
    sortable: bool = False
    selectable: bool = False

    def __post_init__(self) -> None:
        if tuple(sorted(set(self.operators), key=str)) != self.operators:
            raise ValueError("field query operators must be sorted and unique")


@dataclass(frozen=True, slots=True)
class FieldReference:
    target_schema: SemanticId
    target_field: SemanticId


@dataclass(frozen=True, slots=True)
class FieldCapabilities:
    lifecycle: FieldLifecycle = FieldLifecycle()
    query: FieldQuery = FieldQuery()
    reference: FieldReference | None = None
