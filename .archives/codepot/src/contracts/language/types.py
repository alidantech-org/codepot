"""Language type annotation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LanguageTypeKind(StrEnum):
    """Kinds of language type annotations."""

    PRIMITIVE = "primitive"
    ENUM = "enum"
    CLASS = "class"
    INTERFACE = "interface"
    ARRAY = "array"
    MAP = "map"
    UNION = "union"
    OPTIONAL = "optional"
    NULLABLE = "nullable"
    DYNAMIC = "dynamic"
    VOID = "void"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LanguageType:
    """Language-specific type annotation.

    This is used inside ``.lang`` for fields, params, operation inputs, and
    operation outputs.
    """

    kind: LanguageTypeKind
    annotation: str
    display: str

    is_optional: bool = False
    is_nullable: bool = False
    is_array: bool = False
    is_dynamic: bool = False
    is_void: bool = False

    item: LanguageType | None = None
    members: tuple[LanguageType, ...] = ()
