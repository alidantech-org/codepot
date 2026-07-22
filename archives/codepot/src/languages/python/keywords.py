"""Python reserved keyword helpers."""

from __future__ import annotations

from archives.codepot.src.languages.python.constants import PYTHON_RESERVED_WORDS


def is_python_reserved(value: str) -> bool:
    """Return true when value is a Python reserved word."""

    return value in PYTHON_RESERVED_WORDS
