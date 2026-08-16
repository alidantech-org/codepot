from __future__ import annotations

import re

_NON_WORD = re.compile(r"[^A-Za-z0-9]+")


def slug(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("names must be non-empty strings")
    clean = _NON_WORD.sub("-", value.strip()).strip("-").lower()
    if not clean:
        raise ValueError(f"name contains no usable characters: {value!r}")
    return clean


def declaration_id(owner_id: str, kind: str, name: str) -> str:
    return f"{owner_id}/{kind}/{slug(name)}"


def contract_id(name: str) -> str:
    return f"contract/{slug(name)}"


def author_key(name: str, source_id: str | None) -> str:
    return f"{slug(name)}@{source_id or '<memory>'}"


__all__ = ["author_key", "contract_id", "declaration_id", "slug"]
