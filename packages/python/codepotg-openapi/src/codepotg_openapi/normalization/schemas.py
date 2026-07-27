from __future__ import annotations

from codepotg.ir import SemanticId, TypeExpression, TypeKind

from ..parsing.document import ParsedDocument
from ..references.identity import ReferenceIdentity
from ..references.pointer import join_pointer
from .context import NormalizationContext
from .groups import component_group
from .identities import stable_id
from .schema_support import pointer_hint, referenced_group, schema_types


PRIMITIVE_TYPES = {"boolean", "integer", "null", "number", "string"}


def materialize_components(context: NormalizationContext) -> None:
    components = context.root.value.get("components", {})
    if not isinstance(components, dict):
        return
    schemas = components.get("schemas", {})
    if not isinstance(schemas, dict):
        context.diagnostics.error(
            "OA_SCHEMA_COMPONENTS",
            "components.schemas must be an object",
            span=context.root.span("/components/schemas"),
        )
        return
    for name in sorted(schemas):
        context.cancellation.raise_if_cancelled()
        value = schemas[name]
        pointer = join_pointer("/components/schemas", name)
        if not isinstance(value, dict):
            context.diagnostics.error(
                "OA_SCHEMA_SHAPE",
                f"component schema {name!r} must be an object",
                span=context.root.span(pointer),
            )
            continue
        metadata = context.x_codegen.schema(name) if context.x_codegen else None
        if metadata is not None and metadata.role is not None:
            if metadata.role != "dto":
                context.diagnostics.error(
                    "OA_XCODEGEN_SCHEMA_ROLE",
                    f"unsupported controlled schema role {metadata.role!r}",
                    span=context.root.span(metadata.pointer),
                )
            else:
                context.diagnostics.warning(
                    "OA_UNSUPPORTED_SCHEMA_ROLE",
                    "the public core Schema contract has no schema-role field; dto role was preserved only in source metadata",
                    span=context.root.span(metadata.pointer),
                    details=(("coreBlocker", "Schema.role"),),
                )
        semantic_id = materialize_schema(
            context,
            document=context.root,
            pointer=pointer,
            value=value,
            hint=name,
            group=component_group(context, name),
            explicit_id=metadata.id if metadata else None,
        )
        context.schema_by_name[name] = semantic_id
        context.schema_by_name[semantic_id.value] = semantic_id


def materialize_schema(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    value: dict[str, object],
    hint: str,
    group: str,
    explicit_id: str | None = None,
    active: tuple[ReferenceIdentity, ...] = (),
) -> SemanticId:
    key = (document.source.canonical_id, pointer)
    existing = context.schema_by_ref.get(key)
    if existing is not None:
        return existing
    semantic_id = stable_id(
        source=document.source.logical_id,
        category="schema",
        pointer=pointer,
        hint=hint,
        explicit=explicit_id,
    )
    context.schema_by_ref[key] = semantic_id
    context.schema_owner[semantic_id] = group
    current = ReferenceIdentity(document.source.canonical_id, pointer)
    from .schema_builder import build_schema

    schema = build_schema(
        context,
        document=document,
        pointer=pointer,
        value=value,
        hint=hint,
        group=group,
        semantic_id=semantic_id,
        active=(*active, current),
    )
    context.add_schema(group, schema, document, pointer)
    return semantic_id


def schema_type(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    value: dict[str, object],
    hint: str,
    group: str,
    active: tuple[ReferenceIdentity, ...] = (),
) -> TypeExpression:
    reference = value.get("$ref")
    if isinstance(reference, str):
        target = context.resolver.resolve(
            document=document,
            reference=reference,
            expected="schema",
            source_identity=ReferenceIdentity(document.source.canonical_id, pointer),
            active=active,
        )
        if target is None or not isinstance(target.value, dict):
            return TypeExpression(TypeKind.UNKNOWN)
        target_hint = pointer_hint(target.identity.pointer, hint)
        target_id = materialize_schema(
            context,
            document=target.document,
            pointer=target.identity.pointer,
            value=target.value,
            hint=target_hint,
            group=referenced_group(context, target.document, target.identity.pointer, target_hint),
            active=active,
        )
        return TypeExpression.reference_to(target_id)

    type_value = value.get("type")
    nullable, types = schema_types(type_value)
    del nullable
    if "enum" in value or "const" in value or "properties" in value or any(
        key in value for key in ("allOf", "anyOf", "oneOf", "prefixItems")
    ):
        inline_id = materialize_schema(
            context,
            document=document,
            pointer=pointer,
            value=value,
            hint=hint,
            group=group,
            active=active,
        )
        return TypeExpression.reference_to(inline_id)
    if types and len(types) > 1:
        members = tuple(TypeExpression.primitive(item) for item in types)
        return TypeExpression.union_of(*members) if len(members) > 1 else members[0]
    item_type = types[0] if types else None
    if item_type == "array":
        items = value.get("items")
        if isinstance(items, dict):
            return TypeExpression.array_of(
                schema_type(
                    context,
                    document=document,
                    pointer=join_pointer(pointer, "items"),
                    value=items,
                    hint=f"{hint}Item",
                    group=group,
                    active=active,
                )
            )
        context.diagnostics.warning(
            "OA_SCHEMA_ARRAY_ITEMS",
            "array schema has no representable items schema",
            span=document.span(pointer),
        )
        return TypeExpression.array_of(TypeExpression(TypeKind.UNKNOWN))
    if item_type == "object" and "additionalProperties" in value:
        additional = value.get("additionalProperties")
        if isinstance(additional, dict):
            value_type = schema_type(
                context,
                document=document,
                pointer=join_pointer(pointer, "additionalProperties"),
                value=additional,
                hint=f"{hint}Value",
                group=group,
                active=active,
            )
        else:
            value_type = TypeExpression(TypeKind.UNKNOWN)
        return TypeExpression.map_of(TypeExpression.primitive("string"), value_type)
    if item_type in PRIMITIVE_TYPES:
        return TypeExpression.primitive(item_type)
    if item_type == "object":
        inline_id = materialize_schema(
            context,
            document=document,
            pointer=pointer,
            value=value,
            hint=hint,
            group=group,
            active=active,
        )
        return TypeExpression.reference_to(inline_id)
    return TypeExpression(TypeKind.UNKNOWN)
