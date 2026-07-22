"""TypeScript reserved keyword helpers."""

from __future__ import annotations

from archives.codepot.src.languages.typescript.constants import TYPESCRIPT_RESERVED_WORDS


def is_typescript_reserved(value: str) -> bool:
    """Return true when value is a TypeScript reserved word."""

    return value in TYPESCRIPT_RESERVED_WORDS
