from __future__ import annotations

from typing import Any

from constants.openapi import SCHEMA
from inference.models import InferredMediaType, InferredResponse
from openapi.document import OpenApiDocument
from openapi.refs import get_ref
from openapi.resolver.responses import (
    get_response_content,
    get_response_content_types,
    get_response_description,
    get_response_ref,
    get_response_schema_refs,
    is_error_status,
    is_success_status,
    resolve_response,
)


def infer_responses(
    responses: Any,
    document: OpenApiDocument,
) -> tuple[InferredResponse, ...]:
    """Infer responses from operation."""
    if not isinstance(responses, dict):
        return ()

    result: list[InferredResponse] = []

    for status_code, response in responses.items():
        if not isinstance(response, dict):
            continue

        original_ref = get_response_ref(response)
        resolved_response = resolve_response(document, response)

        if resolved_response is None:
            continue

        content = get_response_content(resolved_response)
        content_types = get_response_content_types(resolved_response)
        schema_refs = get_response_schema_refs(resolved_response)
        description = get_response_description(resolved_response)
        media_types = _infer_media_types(content)

        result.append(
            InferredResponse(
                status_code=str(status_code),
                ref=original_ref,
                description=description,
                content_types=content_types,
                media_types=media_types,
                schema_refs=schema_refs,
                is_success=is_success_status(status_code),
                is_error=is_error_status(status_code),
            )
        )

    return tuple(result)


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
