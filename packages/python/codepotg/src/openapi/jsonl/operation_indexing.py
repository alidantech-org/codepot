from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

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
_SEMANTIC_KEYS = {
    "access": "access",
    "accesspolicy": "access",
    "accesspolicies": "access",
    "policy": "access",
    "policies": "access",
    "permission": "permission",
    "permissions": "permission",
    "role": "role",
    "roles": "role",
    "entity": "entity",
    "entities": "entity",
    "targetentity": "entity",
    "sourceentity": "entity",
    "relation": "relation",
    "relations": "relation",
    "relationname": "relation",
    "frontend": "frontend",
    "frontends": "frontend",
    "screen": "screen",
    "screens": "screen",
    "frontendcomponent": "component",
    "componentref": "component",
    "template": "template",
    "templatepath": "template",
    "import": "import",
    "imports": "import",
    "module": "import",
    "output": "generated_file",
    "outputpath": "generated_file",
    "generatedfile": "generated_file",
    "filename": "generated_file",
}
_IDENTITY_KEYS = ("$ref", "ref", "id", "name", "key", "path", "file")


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

    mentions += _register_semantic_mentions(
        record.raw,
        item=classification.key,
        file=location.file,
        indexes=indexes,
    )

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

        mentions += _register_semantic_mentions(
            operation,
            item=operation_key,
            file=location.file,
            indexes=indexes,
            purpose_prefix="operation",
        )

    return mentions, dependencies


def extract_semantic_mentions(value: Any) -> Iterator[tuple[str, str, str]]:
    """Yield small semantic facts without interpreting their full structure."""

    yield from _walk_semantic_mentions(value, path=())


def _register_semantic_mentions(
    value: Any,
    *,
    item: str,
    file: str,
    indexes: ShardedIndexWriter,
    purpose_prefix: str = "record",
) -> int:
    count = 0
    seen: set[tuple[str, str, str]] = set()
    for index, semantic_value, purpose in extract_semantic_mentions(value):
        fact = (index, semantic_value, purpose)
        if fact in seen:
            continue
        seen.add(fact)
        indexes.mention(
            index,
            semantic_value,
            item=item,
            purpose=f"{purpose_prefix}.{purpose}",
            file=file,
        )
        count += 1
    return count


def _walk_semantic_mentions(
    value: Any,
    *,
    path: tuple[str, ...],
) -> Iterator[tuple[str, str, str]]:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = (*path, key)
            normalized = _normalize_key(key)
            index = _SEMANTIC_KEYS.get(normalized)
            if index is not None:
                for semantic_value in _semantic_values(child):
                    yield index, semantic_value, ".".join(child_path)
            yield from _walk_semantic_mentions(child, path=child_path)
    elif isinstance(value, list | tuple):
        for position, child in enumerate(value):
            yield from _walk_semantic_mentions(
                child,
                path=(*path, str(position)),
            )


def _semantic_values(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized and len(normalized) <= 4096:
            yield normalized
        return
    if isinstance(value, list | tuple):
        for item in value:
            yield from _semantic_values(item)
        return
    if not isinstance(value, Mapping):
        return
    for key in _IDENTITY_KEYS:
        candidate = value.get(key)
        if isinstance(candidate, str):
            normalized = candidate.strip()
            if normalized and len(normalized) <= 4096:
                yield normalized


def _normalize_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())
