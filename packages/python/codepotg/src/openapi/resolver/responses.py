from __future__ import annotations

from typing import Any

from constants.openapi import CONTENT, DESCRIPTION
from constants.http import DEFAULT_STATUS_CODE
from openapi.document import OpenApiDocument
from openapi.refs import get_ref
from openapi.resolver.components import resolve_component_ref
from openapi.resolver.content import get_content_schema_refs, get_content_types


def resolve_response(
    document: OpenApiDocument,
    response_node: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Resolve an inline or component-ref OpenAPI response object."""
    if not isinstance(response_node, dict):
        return None

    ref = get_ref(response_node)
    if ref is not None:
        return resolve_component_ref(document, ref)

    return response_node


def get_response_ref(response_node: dict[str, Any] | None) -> str | None:
    """Return the original response ref if the operation uses a component ref."""
    if not isinstance(response_node, dict):
        return None

    ref = get_ref(response_node)
    return ref.raw if ref is not None else None


def get_response_description(response_node: dict[str, Any] | None) -> str:
    """Return a response description."""
    if not isinstance(response_node, dict):
        return ""

    description = response_node.get(DESCRIPTION)
    return str(description) if description is not None else ""


def get_response_content(response_node: dict[str, Any] | None) -> dict[str, Any]:
    """Return the content object from a resolved or inline response."""
    if not isinstance(response_node, dict):
        return {}

    content = response_node.get(CONTENT)
    return content if isinstance(content, dict) else {}


def get_response_content_types(response_node: dict[str, Any] | None) -> tuple[str, ...]:
    """Return content types from a resolved or inline response."""
    return get_content_types(get_response_content(response_node))


def get_response_schema_refs(response_node: dict[str, Any] | None) -> tuple[str, ...]:
    """Return schema refs from a resolved or inline response."""
    return get_content_schema_refs(get_response_content(response_node))


def is_success_status(status_code: str) -> bool:
    return status_code.startswith("2")


def is_error_status(status_code: str) -> bool:
    if status_code == DEFAULT_STATUS_CODE:
        return True

    return not is_success_status(status_code)
