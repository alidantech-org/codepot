"""Python type helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.interface import (
    LanguageTypeFacts,
    LanguageTypeSourceKind,
)
from archives.codepot.src.contracts.language.types import LanguageType, LanguageTypeKind
from archives.codepot.src.languages.python.constants import (
    PRIMITIVE_BOOLEAN,
    PRIMITIVE_INTEGER,
    PRIMITIVE_NUMBER,
    PRIMITIVE_STRING,
    PY_ANY,
    PY_BOOL,
    PY_FLOAT,
    PY_INT,
    PY_NONE,
    PY_STR,
)
from archives.codepot.src.languages.python.syntax import array as py_array
from archives.codepot.src.languages.python.syntax import nullable as py_nullable


def _primitive_annotation(facts: LanguageTypeFacts) -> str:
    """Map primitive facts to Python annotation."""

    if facts.primitive_type == PRIMITIVE_STRING:
        return PY_STR
    if facts.primitive_type == PRIMITIVE_NUMBER:
        return PY_FLOAT
    if facts.primitive_type == PRIMITIVE_INTEGER:
        return PY_INT
    if facts.primitive_type == PRIMITIVE_BOOLEAN:
        return PY_BOOL

    return PY_ANY


def _named_annotation(facts: LanguageTypeFacts) -> str:
    """Map named type facts to Python annotation."""

    if facts.name is None:
        return PY_ANY

    return facts.name.pascal


def _base_annotation(facts: LanguageTypeFacts) -> tuple[LanguageTypeKind, str]:
    """Create base Python annotation from typed facts."""

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

    return LanguageTypeKind.UNKNOWN, PY_ANY


def make_python_type(
    facts: LanguageTypeFacts,
    *,
    is_array: bool = False,
    is_nullable: bool = False,
    is_dynamic: bool = False,
    is_void: bool = False,
) -> LanguageType:
    """Create a Python type annotation."""

    if is_void:
        return LanguageType(
            kind=LanguageTypeKind.VOID,
            annotation=PY_NONE,
            display=PY_NONE,
            is_void=True,
        )

    if is_dynamic:
        current = LanguageType(
            kind=LanguageTypeKind.DYNAMIC,
            annotation=PY_ANY,
            display=PY_ANY,
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
            annotation=py_array(current.annotation),
            display=py_array(current.display),
            is_array=True,
            item=current,
        )

    if is_nullable:
        current = LanguageType(
            kind=LanguageTypeKind.NULLABLE,
            annotation=py_nullable(current.annotation),
            display=py_nullable(current.display),
            is_nullable=True,
            item=current,
        )

    return current
