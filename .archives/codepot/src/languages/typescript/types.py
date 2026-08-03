"""TypeScript type helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.interface import (
    LanguageTypeFacts,
    LanguageTypeSourceKind,
)
from archives.codepot.src.contracts.language.types import LanguageType, LanguageTypeKind
from archives.codepot.src.languages.typescript.constants import (
    PRIMITIVE_BOOLEAN,
    PRIMITIVE_INTEGER,
    PRIMITIVE_NUMBER,
    PRIMITIVE_STRING,
    TS_BOOLEAN,
    TS_NUMBER,
    TS_STRING,
    TS_UNKNOWN,
    TS_VOID,
)
from archives.codepot.src.languages.typescript.syntax import array as ts_array
from archives.codepot.src.languages.typescript.syntax import nullable as ts_nullable


def _primitive_annotation(facts: LanguageTypeFacts) -> str:
    """Map primitive facts to TypeScript annotation."""

    if facts.primitive_type == PRIMITIVE_STRING:
        return TS_STRING
    if facts.primitive_type in {PRIMITIVE_NUMBER, PRIMITIVE_INTEGER}:
        return TS_NUMBER
    if facts.primitive_type == PRIMITIVE_BOOLEAN:
        return TS_BOOLEAN

    return TS_UNKNOWN


def _named_annotation(facts: LanguageTypeFacts) -> str:
    """Map named type facts to TypeScript annotation."""

    if facts.name is None:
        return TS_UNKNOWN

    return facts.name.pascal


def _base_annotation(facts: LanguageTypeFacts) -> tuple[LanguageTypeKind, str]:
    """Create base TypeScript annotation from typed facts."""

    if facts.source_kind == LanguageTypeSourceKind.PRIMITIVE:
        return LanguageTypeKind.PRIMITIVE, _primitive_annotation(facts)

    if facts.source_kind == LanguageTypeSourceKind.ENUM:
        return LanguageTypeKind.ENUM, _named_annotation(facts)

    if facts.source_kind in {
        LanguageTypeSourceKind.COMPOSITE,
        LanguageTypeSourceKind.MODEL,
        LanguageTypeSourceKind.DTO,
    }:
        return LanguageTypeKind.INTERFACE, _named_annotation(facts)

    return LanguageTypeKind.UNKNOWN, TS_UNKNOWN


def make_typescript_type(
    facts: LanguageTypeFacts,
    *,
    is_array: bool = False,
    is_nullable: bool = False,
    is_dynamic: bool = False,
    is_void: bool = False,
) -> LanguageType:
    """Create a TypeScript type annotation."""

    if is_void:
        return LanguageType(
            kind=LanguageTypeKind.VOID,
            annotation=TS_VOID,
            display=TS_VOID,
            is_void=True,
        )

    if is_dynamic:
        current = LanguageType(
            kind=LanguageTypeKind.DYNAMIC,
            annotation=TS_UNKNOWN,
            display=TS_UNKNOWN,
            is_dynamic=True,
        )
    else:
        kind, annotation = _base_annotation(facts)
        current = LanguageType(
            kind=kind,
            annotation=annotation,
            display=annotation,
        )

    if is_array:
        current = LanguageType(
            kind=LanguageTypeKind.ARRAY,
            annotation=ts_array(current.annotation),
            display=ts_array(current.display),
            is_array=True,
            item=current,
        )

    if is_nullable:
        current = LanguageType(
            kind=LanguageTypeKind.NULLABLE,
            annotation=ts_nullable(current.annotation),
            display=ts_nullable(current.display),
            is_nullable=True,
            item=current,
        )

    return current
