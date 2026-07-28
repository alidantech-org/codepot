from __future__ import annotations

from codepotg.ir import Name, OperationFailure, OperationOutput

from ..parsing.document import ParsedDocument
from ..references.pointer import join_pointer
from .context import NormalizationContext, OperationBuilder
from .operation_support import (
    resolve_mapping,
    schema_from_content_with_media,
    schema_id_for_use,
)
from .provenance import kernel_data, selected_raw


def normalize_responses(
    context: NormalizationContext,
    operation: OperationBuilder,
    *,
    document: ParsedDocument,
    pointer: str,
    group: str,
    raw: object,
) -> None:
    responses_pointer = join_pointer(pointer, "responses")
    if not isinstance(raw, dict):
        context.diagnostics.error(
            "OA_OPERATION_RESPONSES",
            "operation responses must be an object",
            span=document.span(responses_pointer),
        )
        return
    for status in sorted(raw, key=status_sort_key):
        response_pointer = join_pointer(responses_pointer, status)
        resolved = resolve_mapping(
            context,
            document=document,
            pointer=response_pointer,
            raw=raw[status],
            expected="response",
        )
        if resolved is None:
            continue
        item_document, item_pointer, response = resolved
        schema, schema_pointer, media_types = schema_from_content_with_media(
            context,
            document=item_document,
            pointer=join_pointer(item_pointer, "content"),
            content=response.get("content"),
            owner=f"response {status}",
            allow_empty=True,
        )
        schema_id = (
            schema_id_for_use(
                context,
                document=item_document,
                pointer=schema_pointer,
                schema=schema,
                hint=f"{operation.name.value}Status{status}Output",
                group=group,
            )
            if schema is not None
            else None
        )
        response_raw = {
            "status": status,
            "mediaTypes": list(media_types),
            **selected_raw(response, "headers", "links"),
        }
        response_data = kernel_data(
            item_document,
            item_pointer,
            options=context.options,
            diagnostics=context.diagnostics,
            raw={"http": response_raw},
        )
        if is_success(status):
            operation.outputs.append(
                OperationOutput(
                    name=Name(f"status {status}"),
                    schema=schema_id,
                    optional=False,
                    data=response_data,
                )
            )
        else:
            description = response.get("description")
            operation.failures.append(
                OperationFailure(
                    code=status,
                    schema=schema_id,
                    message=description if isinstance(description, str) else None,
                    data=response_data,
                )
            )
        context.diagnostics.warning(
            "OA_UNSUPPORTED_HTTP_RESPONSE_DETAILS",
            f"response {status} status/media/header facts are preserved but not represented by the current public HttpFacet",
            span=item_document.span(item_pointer),
            details=(("coreBlocker", "HttpFacet response bindings"),),
        )


def is_success(status: str) -> bool:
    upper = status.upper()
    return (
        len(upper) == 3
        and upper.startswith("2")
        and all(char.isdigit() or char == "X" for char in upper)
    )


def status_sort_key(value: str) -> tuple[int, str]:
    return (0 if value.isdigit() else 1, value)
