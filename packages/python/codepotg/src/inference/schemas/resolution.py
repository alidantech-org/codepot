"""Schema alias resolution.

This module provides utilities for resolving schema alias chains
to make inferred schemas self-contained for emitters.
"""

from typing import Any

from constants.openapi import REF_SCHEMAS
from openapi.document import OpenApiDocument
from openapi.refs import get_ref


def resolve_schema_alias(document: OpenApiDocument, schema: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve a schema alias chain to get the effective schema.

    Follows local schema $ref chains until a non-ref schema is found.
    Used to infer type/format/enum values for alias schemas.

    Args:
        document: The OpenAPI document.
        schema: A schema object that may be a $ref alias.

    Returns:
        The resolved schema dict, or None if resolution fails.
    """
    current = schema
    seen_refs: set[str] = set()

    while isinstance(current, dict):
        ref_info = get_ref(current)

        if not ref_info or not ref_info.is_component:
            # Not a ref or not a component ref - this is the effective schema
            return current

        if ref_info.raw in seen_refs:
            # Cycle detected - return current to avoid infinite loop
            return current

        seen_refs.add(ref_info.raw)

        # Extract schema name from ref path
        if ref_info.raw.startswith(REF_SCHEMAS):
            schema_name = ref_info.raw[len(REF_SCHEMAS) :]
            resolved = document.schemas.get(schema_name)

            if not isinstance(resolved, dict):
                # Resolution failed - return current
                return current

            current = resolved
        else:
            # Non-component ref - can't resolve
            return current

    return current


def resolve_schema_alias_ref(document: OpenApiDocument, schema: dict[str, Any]) -> str | None:
    """Get the resolved ref for a schema alias chain.

    Args:
        document: The OpenAPI document.
        schema: A schema object that may be a $ref alias.

    Returns:
        The final resolved ref string, or None if not a ref.
    """
    ref_info = get_ref(schema)
    if ref_info and ref_info.is_component:
        return ref_info.raw
    return None


def resolve_schema_alias_chain(document: OpenApiDocument, schema: dict[str, Any]) -> tuple[str, ...]:
    """Get the full chain of refs for a schema alias.

    Args:
        document: The OpenAPI document.
        schema: A schema object that may be a $ref alias.

    Returns:
        A tuple of ref strings in the alias chain.
    """
    chain: list[str] = []
    current = schema
    seen_refs: set[str] = set()

    while isinstance(current, dict):
        ref_info = get_ref(current)

        if not ref_info or not ref_info.is_component:
            break

        if ref_info.raw in seen_refs:
            # Cycle detected
            break

        seen_refs.add(ref_info.raw)
        chain.append(ref_info.raw)

        # Extract schema name from ref path
        if ref_info.raw.startswith(REF_SCHEMAS):
            schema_name = ref_info.raw[len(REF_SCHEMAS) :]
            resolved = document.schemas.get(schema_name)

            if not isinstance(resolved, dict):
                break

            current = resolved
        else:
            break

    return tuple(chain)
