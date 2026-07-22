from __future__ import annotations

from inference.models import InferredOperation


def collect_operation_dependencies(operation: InferredOperation) -> tuple[str, ...]:
    """Collect all schema refs reachable through operation components."""
    refs: set[str] = set()

    # From parameters
    for param in operation.parameters:
        if param.schema_ref:
            refs.add(param.schema_ref)
        refs.update(param.schema_refs)

    # From request body
    if operation.request_body:
        refs.update(operation.request_body.schema_refs)
        for media_type in operation.request_body.media_types:
            if media_type.schema_ref:
                refs.add(media_type.schema_ref)
            refs.update(media_type.schema_refs)

    # From responses
    for response in operation.responses:
        refs.update(response.schema_refs)
        for media_type in response.media_types:
            if media_type.schema_ref:
                refs.add(media_type.schema_ref)
            refs.update(media_type.schema_refs)

    return tuple(sorted(refs))
