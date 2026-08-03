"""Case conversion utilities for generated names."""

from __future__ import annotations

import re

_WORD_BOUNDARY_PATTERN = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_SAFE_SEGMENT_PATTERN = re.compile(r"[^a-zA-Z0-9_./-]+")


def split_words(value: str) -> list[str]:
    """Split a name into lowercase words."""
    if not value:
        return []

    spaced = _WORD_BOUNDARY_PATTERN.sub(" ", value)
    spaced = re.sub(r"[_\-.\/]+", " ", spaced)
    spaced = re.sub(r"\s+", " ", spaced).strip()

    return [word.lower() for word in spaced.split(" ") if word]


def clean_name(value: str) -> str:
    """Return a readable cleaned name."""
    return " ".join(split_words(value))


def snake_case(value: str) -> str:
    """Return snake_case."""
    return "_".join(split_words(value))


def kebab_case(value: str) -> str:
    """Return kebab-case."""
    return "-".join(split_words(value))


def camel_case(value: str) -> str:
    """Return camelCase."""
    words = split_words(value)
    if not words:
        return ""
    return words[0] + "".join(word.capitalize() for word in words[1:])


def pascal_case(value: str) -> str:
    """Return PascalCase."""
    return "".join(word.capitalize() for word in split_words(value))


def screaming_case(value: str) -> str:
    """Return SCREAMING_SNAKE_CASE."""
    return snake_case(value).upper()


def constant_case(value: str) -> str:
    """Return lower constant-style identifier."""
    return snake_case(value)


def dot_case(value: str) -> str:
    """Return dot.case."""
    return ".".join(split_words(value))


def path_case(value: str) -> str:
    """Return a safe path segment."""
    safe = _SAFE_SEGMENT_PATTERN.sub("_", snake_case(value))
    safe = safe.strip("._-/")
    return safe or "unnamed"


def lower_case(value: str) -> str:
    """Return lower case."""
    return clean_name(value).lower()


def upper_case(value: str) -> str:
    """Return upper case."""
    return clean_name(value).upper()
