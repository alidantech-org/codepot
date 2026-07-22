from __future__ import annotations

from typing import Any

from constants.openapi import CONTENT, REQUIRED
from openapi.document import OpenApiDocument
from openapi.refs import get_ref
from openapi.resolver.components import resolve_component_ref
from openapi.resolver.content import get_content_schema_refs, get_content_types


def resolve_request_body(
    document: OpenApiDocument,
    request_body_node: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Resolve an inline or component-ref OpenAPI requestBody object."""
    if not isinstance(request_body_node, dict):
        return None

    ref = get_ref(request_body_node)
    if ref is not None:
        return resolve_component_ref(document, ref)

    return request_body_node


def get_request_body_ref(request_body_node: dict[str, Any] | None) -> str | None:
    """Return the original requestBody ref if the operation uses a component ref."""
    if not isinstance(request_body_node, dict):
        return None

    ref = get_ref(request_body_node)
    return ref.raw if ref is not None else None


def is_request_body_required(request_body_node: dict[str, Any] | None) -> bool:
    """Return whether a resolved or inline requestBody is required."""
    if not isinstance(request_body_node, dict):
        return False

    return bool(request_body_node.get(REQUIRED, False))


def get_request_body_content(
    request_body_node: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return the content object from a resolved or inline requestBody."""
    if not isinstance(request_body_node, dict):
        return {}

    content = request_body_node.get(CONTENT)
    return content if isinstance(content, dict) else {}


def get_request_body_content_types(
    request_body_node: dict[str, Any] | None,
) -> tuple[str, ...]:
    """Return content types from a resolved or inline requestBody."""
    return get_content_types(get_request_body_content(request_body_node))


def get_request_body_schema_refs(
    request_body_node: dict[str, Any] | None,
) -> tuple[str, ...]:
    """Return schema refs from a resolved or inline requestBody."""
    return get_content_schema_refs(get_request_body_content(request_body_node))
