from __future__ import annotations

import json

from codepotg.ir import (
    Name,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    TypeExpression,
    TypeKind,
)

from ..parsing.document import ParsedDocument
from ..references.identity import ReferenceIdentity
from ..references.pointer import join_pointer
from .context import NormalizationContext
from .identities import stable_id
from .provenance import extension_values, kernel_data, selected_raw
from .schema_support import field_constraints, pointer_hint, referenced_group, schema_types, title


PRIMITIVE_TYPES = {"boolean", "integer", "null", "number", "string"}


def build_schema(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    value: dict[str, object],
    hint: str,
    group: str,
    semantic_id: SemanticId,
    active: tuple[ReferenceIdentity, ...],
) -> Schema:
    from .schemas import materialize_schema, schema_type

    raw = selected_raw(
        value,
        "default",
        "deprecated",
        "description",
        "example",
        "examples",
        "readOnly",
        "writeOnly",
        "xml",
    )
    extensions = extension_values(value) if context.options.preserve_unknown_extensions else {}
    data = kernel_data(
        document,
        pointer,
        options=context.options,
        diagnostics=context.diagnostics,
        raw=raw,
        extensions=extensions,
    )

    reference = value.get("$ref")
    if isinstance(reference, str):
        target = context.resolver.resolve(
            document=document,
            reference=reference,
            expected="schema",
            source_identity=ReferenceIdentity(document.source.canonical_id, pointer),
            active=active,
        )
        target_type = TypeExpression(TypeKind.UNKNOWN)
        if target is not None and isinstance(target.value, dict):
            target_hint = pointer_hint(target.identity.pointer, hint)
            target_id = context.schema_by_ref.get(
                (target.document.source.canonical_id, target.identity.pointer)
            )
            if target_id is None:
                target_id = materialize_schema(
                    context,
                    document=target.document,
                    pointer=target.identity.pointer,
                    value=target.value,
                    hint=target_hint,
                    group=referenced_group(
                        context, target.document, target.identity.pointer, target_hint
                    ),
                    active=active,
                )
            target_type = TypeExpression.reference_to(target_id)
        if len(value) > 1:
            context.diagnostics.warning(
                "OA_SCHEMA_REF_SIBLINGS",
                "$ref sibling keywords were preserved but not merged into the alias schema",
                span=document.span(pointer),
            )
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.ALIAS,
            alias_of=target_type,
            data=data,
        )

    if "const" in value:
        literal = value.get("const")
        if literal is None or isinstance(literal, str | bool | int | float):
            return Schema(
                id=semantic_id,
                name=Name(hint),
                kind=SchemaKind.LITERAL,
                literal=literal,
                data=data,
            )

    enum = value.get("enum")
    if isinstance(enum, list) and enum:
        values: list[str] = []
        for item in enum:
            if isinstance(item, str):
                values.append(item)
            else:
                values.append(json.dumps(item, sort_keys=True, separators=(",", ":")))
                context.diagnostics.warning(
                    "OA_SCHEMA_ENUM_STRING_ENCODING",
                    "non-string enum value was encoded canonically because the public core enum contract stores strings",
                    span=document.span(join_pointer(pointer, "enum")),
                    details=(("coreBlocker", "Schema.enum_values literal typing"),),
                )
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.ENUM,
            enum_values=tuple(values),
            data=data,
        )

    for key, kind, constructor in (
        ("allOf", SchemaKind.INTERSECTION, TypeExpression.intersection_of),
        ("oneOf", SchemaKind.UNION, TypeExpression.union_of),
        ("anyOf", SchemaKind.UNION, TypeExpression.union_of),
    ):
        members_raw = value.get(key)
        if isinstance(members_raw, list) and members_raw:
            members = tuple(
                schema_type(
                    context,
                    document=document,
                    pointer=join_pointer(pointer, key, index),
                    value=item if isinstance(item, dict) else {},
                    hint=f"{hint}{key.title()}{index + 1}",
                    group=group,
                    active=active,
                )
                for index, item in enumerate(members_raw)
            )
            expression = members[0] if len(members) == 1 else constructor(*members)
            if key == "anyOf":
                context.diagnostics.warning(
                    "OA_SCHEMA_ANYOF_UNION",
                    "anyOf was represented as a structural union; validation-overlap semantics remain in raw source data",
                    span=document.span(join_pointer(pointer, key)),
                )
            return Schema(
                id=semantic_id,
                name=Name(hint),
                kind=SchemaKind.ALIAS if len(members) == 1 else kind,
                alias_of=expression,
                data=data,
            )

    prefix = value.get("prefixItems")
    if isinstance(prefix, list) and prefix:
        members = tuple(
            schema_type(
                context,
                document=document,
                pointer=join_pointer(pointer, "prefixItems", index),
                value=item if isinstance(item, dict) else {},
                hint=f"{hint}Item{index + 1}",
                group=group,
                active=active,
            )
            for index, item in enumerate(prefix)
        )
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.TUPLE,
            alias_of=TypeExpression.tuple_of(*members),
            data=data,
        )

    nullable, types = schema_types(value.get("type"))
    del nullable
    if len(types) > 1:
        members = tuple(TypeExpression.primitive(item) for item in types)
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.UNION,
            alias_of=TypeExpression.union_of(*members),
            data=data,
        )
    type_value = types[0] if types else None

    properties = value.get("properties")
    if type_value == "object" or isinstance(properties, dict):
        if not isinstance(properties, dict):
            properties = {}
        required_raw = value.get("required", [])
        required = set(required_raw) if isinstance(required_raw, list) else set()
        if not all(isinstance(item, str) for item in required):
            context.diagnostics.error(
                "OA_SCHEMA_REQUIRED",
                "schema required must be an array of property names",
                span=document.span(join_pointer(pointer, "required")),
            )
            required = set()
        fields: list[SchemaField] = []
        for field_name in sorted(properties):
            field_value = properties[field_name]
            field_pointer = join_pointer(pointer, "properties", field_name)
            if not isinstance(field_value, dict):
                context.diagnostics.error(
                    "OA_SCHEMA_FIELD",
                    f"schema property {field_name!r} must be an object",
                    span=document.span(field_pointer),
                )
                continue
            field_type = schema_type(
                context,
                document=document,
                pointer=field_pointer,
                value=field_value,
                hint=f"{hint}{title(field_name)}",
                group=group,
                active=active,
            )
            field_nullable, _ = schema_types(field_value.get("type"))
            field_nullable = field_nullable or field_value.get("nullable") is True
            field_id = stable_id(
                source=document.source.logical_id,
                category="field",
                pointer=field_pointer,
                hint=f"{hint}-{field_name}",
            )
            context.field_by_name[(semantic_id, field_name)] = field_id
            if field_value.get("writeOnly") is True:
                context.diagnostics.warning(
                    "OA_UNSUPPORTED_WRITE_ONLY",
                    "writeOnly is not represented by the current public SchemaField contract and remains in raw metadata",
                    span=document.span(field_pointer),
                    details=(("coreBlocker", "SchemaField.writeonly"),),
                )
            fields.append(
                SchemaField(
                    id=field_id,
                    name=Name(field_name),
                    type=field_type,
                    required=field_name in required,
                    nullable=field_nullable,
                    readonly=field_value.get("readOnly") is True,
                    constraints=field_constraints(field_value),
                    data=kernel_data(
                        document,
                        field_pointer,
                        options=context.options,
                        diagnostics=context.diagnostics,
                        raw=selected_raw(
                            field_value,
                            "default",
                            "deprecated",
                            "description",
                            "example",
                            "examples",
                            "writeOnly",
                        ),
                        extensions=(
                            extension_values(field_value)
                            if context.options.preserve_unknown_extensions
                            else {}
                        ),
                    ),
                )
            )
        if not fields and "additionalProperties" in value:
            additional = value.get("additionalProperties")
            value_type = (
                schema_type(
                    context,
                    document=document,
                    pointer=join_pointer(pointer, "additionalProperties"),
                    value=additional,
                    hint=f"{hint}Value",
                    group=group,
                    active=active,
                )
                if isinstance(additional, dict)
                else TypeExpression(TypeKind.UNKNOWN)
            )
            return Schema(
                id=semantic_id,
                name=Name(hint),
                kind=SchemaKind.MAP,
                alias_of=TypeExpression.map_of(
                    TypeExpression.primitive("string"), value_type
                ),
                data=data,
            )
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.OBJECT,
            fields=tuple(fields),
            data=data,
        )

    if type_value == "array":
        items = value.get("items")
        item_type = (
            schema_type(
                context,
                document=document,
                pointer=join_pointer(pointer, "items"),
                value=items,
                hint=f"{hint}Item",
                group=group,
                active=active,
            )
            if isinstance(items, dict)
            else TypeExpression(TypeKind.UNKNOWN)
        )
        if not isinstance(items, dict):
            context.diagnostics.warning(
                "OA_SCHEMA_ARRAY_ITEMS",
                "array schema has no representable items schema",
                span=document.span(pointer),
            )
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.ARRAY,
            item_type=item_type,
            data=data,
        )

    if type_value in PRIMITIVE_TYPES:
        return Schema(
            id=semantic_id,
            name=Name(hint),
            kind=SchemaKind.PRIMITIVE,
            alias_of=TypeExpression.primitive(type_value),
            data=data,
        )

    context.diagnostics.warning(
        "OA_SCHEMA_UNKNOWN",
        f"schema {hint!r} has no supported structural kind",
        span=document.span(pointer),
    )
    return Schema(
        id=semantic_id,
        name=Name(hint),
        kind=SchemaKind.UNKNOWN,
        data=data,
    )
