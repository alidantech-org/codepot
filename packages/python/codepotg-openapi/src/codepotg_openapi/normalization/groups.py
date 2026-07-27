from __future__ import annotations

from ..options import MultiTagPolicy
from ..references.pointer import join_pointer
from .context import NormalizationContext


HTTP_METHODS = ("delete", "get", "head", "options", "patch", "post", "put", "trace")


def prepare_groups(context: NormalizationContext) -> None:
    if context.x_codegen is not None:
        for group in context.x_codegen.groups:
            context.ensure_group(
                group.name,
                pointer=group.pointer,
                explicit_id=group.id,
            )
    tags = context.root.value.get("tags")
    if isinstance(tags, list):
        for index, item in enumerate(tags):
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                name = item["name"]
                explicit = context.x_codegen.group(name) if context.x_codegen else None
                context.ensure_group(
                    name,
                    pointer=join_pointer("/tags", index),
                    explicit_id=explicit.id if explicit else None,
                )


def component_group(context: NormalizationContext, schema_name: str) -> str:
    metadata = context.x_codegen.schema(schema_name) if context.x_codegen else None
    return metadata.group if metadata and metadata.group else "shared"


def operation_group(
    context: NormalizationContext,
    operation: dict[str, object],
    *,
    operation_key: str,
    method: str,
    path: str,
    pointer: str,
) -> str:
    metadata = context.x_codegen.operation(operation_key) if context.x_codegen else None
    if metadata is None and context.x_codegen is not None:
        metadata = context.x_codegen.operation(f"{method.upper()} {path}")
    if metadata is not None and metadata.group:
        context.ensure_group(metadata.group, pointer=metadata.pointer)
        return metadata.group

    tags = operation.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
        context.diagnostics.error(
            "OA_GROUP_TAGS",
            "operation tags must be an array of strings",
            span=context.root.span(join_pointer(pointer, "tags")),
        )
        tags = []
    if len(tags) > 1:
        if context.options.multi_tag_policy is MultiTagPolicy.EXPLICIT_REQUIRED:
            context.diagnostics.error(
                "OA_GROUP_MULTITAG_EXPLICIT_REQUIRED",
                "multi-tag operation requires explicit x-codegen group ownership",
                span=context.root.span(join_pointer(pointer, "tags")),
                details=(("tags", tuple(tags)),),
            )
            return "default"
        context.diagnostics.warning(
            "OA_GROUP_MULTITAG_FIRST",
            f"multi-tag operation is owned by first tag {tags[0]!r} and is not cloned",
            span=context.root.span(join_pointer(pointer, "tags")),
            details=(("tags", tuple(tags)),),
        )
    if tags:
        context.ensure_group(tags[0], pointer=join_pointer(pointer, "tags", 0))
        return tags[0]
    context.ensure_group("default", pointer=pointer)
    return "default"
