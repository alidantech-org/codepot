from __future__ import annotations

from typing import Any

from constants.openapi import SCHEMA
from openapi.refs import find_refs, get_ref

def get_content_types(content: dict[str, Any] | None) -> tuple[str, ...]:
    """Return media type keys from a standard OpenAPI content object."""
    if not isinstance(content, dict):
        return ()

    return tuple(str(content_type) for content_type in content.keys())


def get_media_type(
    content: dict[str, Any] | None,
    content_type: str,
) -> dict[str, Any] | None:
    """Return one media type object from a standard OpenAPI content object."""
    if not isinstance(content, dict):
        return None

    media_type = content.get(content_type)
    if not isinstance(media_type, dict):
        return None

    return media_type


def get_media_schema_ref(media_type: dict[str, Any] | None) -> str | None:
    """Return the direct schema ref from one media type object, if present."""
    if not isinstance(media_type, dict):
        return None

    schema = media_type.get(SCHEMA)
    ref = get_ref(schema)

    if ref is None:
        return None

    return ref.raw


def get_media_schema_refs(media_type: dict[str, Any] | None) -> tuple[str, ...]:
    """Return all schema refs reachable from one media type schema object."""
    if not isinstance(media_type, dict):
        return ()

    schema = media_type.get(SCHEMA)
    return tuple(ref.raw for ref in find_refs(schema))


def get_content_schema_refs(content: dict[str, Any] | None) -> tuple[str, ...]:
    """Return all schema refs from every media type in a content object."""
    if not isinstance(content, dict):
        return ()

    refs: list[str] = []

    for media_type in content.values():
        if not isinstance(media_type, dict):
            continue

        refs.extend(get_media_schema_refs(media_type))

    return tuple(_dedupe(refs))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result
