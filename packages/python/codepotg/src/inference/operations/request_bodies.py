from __future__ import annotations

from typing import Any

from constants.openapi import SCHEMA
from inference.models import InferredMediaType, InferredRequestBody
from openapi.document import OpenApiDocument
from openapi.refs import get_ref
from openapi.resolver.request_bodies import (
    get_request_body_content,
    get_request_body_content_types,
    get_request_body_schema_refs,
    get_request_body_ref,
    is_request_body_required,
    resolve_request_body,
)


def infer_request_body(
    request_body: Any,
    document: OpenApiDocument,
) -> InferredRequestBody | None:
    """Infer request body from operation."""
    if not isinstance(request_body, dict):
        return None

    original_ref = get_request_body_ref(request_body)
    resolved_request_body = resolve_request_body(document, request_body)

    if resolved_request_body is None:
        return None

    content = get_request_body_content(resolved_request_body)
    content_types = get_request_body_content_types(resolved_request_body)
    schema_refs = get_request_body_schema_refs(resolved_request_body)
    required = is_request_body_required(resolved_request_body)
    media_types = _infer_media_types(content)

    return InferredRequestBody(
        ref=original_ref,
        required=required,
        content_types=content_types,
        media_types=media_types,
        schema_refs=schema_refs,
    )


def _infer_media_types(content: dict[str, Any] | None) -> tuple[InferredMediaType, ...]:
    """Infer media types from content object."""
    if not isinstance(content, dict):
        return ()

    result: list[InferredMediaType] = []

    for content_type, media_content in content.items():
        if not isinstance(media_content, dict):
            continue

        schema = media_content.get(SCHEMA)
        ref = get_ref(schema)

        result.append(
            InferredMediaType(
                content_type=content_type,
                schema_ref=ref.raw if ref else None,
                schema_refs=tuple([ref.raw]) if ref else (),
            )
        )

    return tuple(result)
