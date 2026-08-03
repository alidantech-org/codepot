"""Dart type helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.interface import (
    LanguageTypeFacts,
    LanguageTypeSourceKind,
)
from archives.codepot.src.contracts.language.types import LanguageType, LanguageTypeKind
from archives.codepot.src.languages.dart.constants import (
    DART_BOOL,
    DART_DOUBLE,
    DART_DYNAMIC,
    DART_INT,
    DART_STRING,
    DART_VOID,
    PRIMITIVE_BOOLEAN,
    PRIMITIVE_INTEGER,
    PRIMITIVE_NUMBER,
    PRIMITIVE_STRING,
)
from archives.codepot.src.languages.dart.syntax import array as dart_array
from archives.codepot.src.languages.dart.syntax import nullable as dart_nullable


def _primitive_annotation(facts: LanguageTypeFacts) -> str:
    """Map primitive facts to Dart annotation."""

    if facts.primitive_type == PRIMITIVE_STRING:
        return DART_STRING
    if facts.primitive_type == PRIMITIVE_NUMBER:
        return DART_DOUBLE
    if facts.primitive_type == PRIMITIVE_INTEGER:
        return DART_INT
    if facts.primitive_type == PRIMITIVE_BOOLEAN:
        return DART_BOOL

    return DART_DYNAMIC


def _named_annotation(facts: LanguageTypeFacts) -> str:
    """Map named type facts to Dart annotation."""

    if facts.name is None:
        return DART_DYNAMIC

    return facts.name.pascal


def _base_annotation(facts: LanguageTypeFacts) -> tuple[LanguageTypeKind, str]:
    """Create base Dart annotation from typed facts."""

    if facts.source_kind == LanguageTypeSourceKind.PRIMITIVE:
        return LanguageTypeKind.PRIMITIVE, _primitive_annotation(facts)

    if facts.source_kind == LanguageTypeSourceKind.ENUM:
        return LanguageTypeKind.ENUM, _named_annotation(facts)

    if facts.source_kind in {
        LanguageTypeSourceKind.COMPOSITE,
        LanguageTypeSourceKind.MODEL,
        LanguageTypeSourceKind.DTO,
    }:
        return LanguageTypeKind.CLASS, _named_annotation(facts)

    return LanguageTypeKind.UNKNOWN, DART_DYNAMIC


def make_dart_type(
    facts: LanguageTypeFacts,
    *,
    is_array: bool = False,
    is_nullable: bool = False,
    is_dynamic: bool = False,
    is_void: bool = False,
) -> LanguageType:
    """Create a Dart type annotation."""

    if is_void:
        return LanguageType(
            kind=LanguageTypeKind.VOID,
            annotation=DART_VOID,
            display=DART_VOID,
            is_void=True,
        )

    if is_dynamic:
        current = LanguageType(
            kind=LanguageTypeKind.DYNAMIC,
            annotation=DART_DYNAMIC,
            display=DART_DYNAMIC,
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
            annotation=dart_array(current.annotation),
            display=dart_array(current.display),
            is_array=True,
            item=current,
        )

    if is_nullable:
        current = LanguageType(
            kind=LanguageTypeKind.NULLABLE,
            annotation=dart_nullable(current.annotation),
            display=dart_nullable(current.display),
            is_nullable=True,
            item=current,
        )

    return current
