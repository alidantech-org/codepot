from __future__ import annotations

from collections.abc import Mapping

from .indexing import (
    ClassifiedRecord,
    ShardedIndexWriter,
    extract_explicit_resource_mentions,
    extract_ref_mentions,
    extract_tag_mentions,
)
from .models import ExtractedRecord, RecordLocation

_HTTP_METHODS = frozenset(
    {"get", "put", "post", "delete", "patch", "options", "head", "trace"}
)


def register_additional_indexes(
    record: ExtractedRecord,
    classification: ClassifiedRecord,
    location: RecordLocation,
    *,
    indexes: ShardedIndexWriter,
) -> tuple[int, int]:
    """Register cheap selection facts and exact operation-level usages."""

    mentions = 0
    dependencies = 0

    indexes.mention(
        "section",
        record.section,
        item=classification.key,
        purpose="record.section",
        file=location.file,
    )
    mentions += 1

    if classification.kind:
        indexes.mention(
            "kind",
            classification.kind,
            item=classification.key,
            purpose="record.kind",
            file=location.file,
        )
        mentions += 1

    if record.section != "paths" or not isinstance(record.raw, Mapping):
        return mentions, dependencies

    for method, operation in record.raw.items():
        lowered = str(method).lower()
        if lowered not in _HTTP_METHODS or not isinstance(operation, Mapping):
            continue

        operation_key = f"operation:{lowered}:{record.name}"
        indexes.mention(
            "kind",
            "operation",
            item=operation_key,
            purpose="operation.kind",
            file=location.file,
        )
        indexes.mention(
            "method",
            lowered,
            item=operation_key,
            purpose="operation.method",
            file=location.file,
        )
        mentions += 2

        operation_resources = set(classification.resources)
        operation_resources.update(
            resource for resource, _ in extract_explicit_resource_mentions(operation)
        )
        for resource in sorted(operation_resources):
            indexes.mention(
                "resource",
                resource,
                item=operation_key,
                purpose="operation.resource",
                file=location.file,
            )
            mentions += 1

        for ref, purpose in extract_ref_mentions(operation):
            indexes.mention(
                "ref",
                ref,
                item=operation_key,
                purpose=purpose,
                file=location.file,
            )
            indexes.dependency(
                source=operation_key,
                target=ref,
                purpose=purpose,
                file=location.file,
            )
            mentions += 1
            dependencies += 1

        for tag, purpose in extract_tag_mentions(operation):
            indexes.mention(
                "tag",
                tag,
                item=operation_key,
                purpose=purpose,
                file=location.file,
            )
            mentions += 1

    return mentions, dependencies
