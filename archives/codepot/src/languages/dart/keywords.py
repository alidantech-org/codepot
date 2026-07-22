"""Dart reserved keyword helpers."""

from __future__ import annotations

from archives.codepot.src.languages.dart.constants import DART_RESERVED_WORDS


def is_dart_reserved(value: str) -> bool:
    """Return true when value is a Dart reserved word."""

    return value in DART_RESERVED_WORDS
