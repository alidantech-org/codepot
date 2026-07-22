"""Dart dependency fact builders."""

from __future__ import annotations

from contracts.api import ApiField, ApiSchema, ApiSchemaKind
from contracts.template import (
    TemplateDependency,
    TemplateDependencyPurpose,
    TemplateDependencyTarget,
    TemplateDependencyTargetKind,
)


def schema_dependencies(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Build schema dependencies for Dart emission."""
    dependencies: list[TemplateDependency] = []
    seen_refs: set[str] = set()

    for ref in schema.inherited_refs:
        _append_dependency(
            dependencies,
            seen_refs,
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.INHERITANCE,
                reason=f"{schema.name.pascal.o} inherits from {ref}",
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
                is_inheritance=True,
            ),
        )

    for field in _inherited_constructor_fields(schema, schema_by_ref):
        for inherited_dependency in field_dependencies(field, schema_by_ref):
            _append_dependency(
                dependencies,
                seen_refs,
                TemplateDependency(
                    ref=inherited_dependency.ref,
                    purpose=inherited_dependency.purpose,
                    reason=(
                        f"Inherited constructor field {field.name.camel.o} "
                        f"uses {inherited_dependency.ref}"
                    ),
                    target=inherited_dependency.target,
                    is_self=inherited_dependency.is_self,
                    is_importable=inherited_dependency.is_importable,
                ),
            )

    for ref in schema.dependencies:
        if ref in schema.inherited_refs:
            continue

        _append_dependency(
            dependencies,
            seen_refs,
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=f"{schema.name.pascal.o} references {ref}",
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
            ),
        )

    return tuple(dependencies)


def _append_dependency(
    dependencies: list[TemplateDependency],
    seen_refs: set[str],
    item: TemplateDependency,
) -> None:
    if item.ref in seen_refs:
        return

    seen_refs.add(item.ref)
    dependencies.append(item)


def _inherited_constructor_fields(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[ApiField, ...]:
    fields: list[ApiField] = []

    for ref in schema.inherited_refs:
        base_schema = schema_by_ref.get(ref)
        if base_schema is None:
            continue

        fields.extend(_constructor_fields(base_schema, schema_by_ref))

    return tuple(fields)


def _constructor_fields(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
    seen_refs: frozenset[str] = frozenset(),
) -> tuple[ApiField, ...]:
    if schema.ref in seen_refs:
        return schema.fields

    base_schema = _base_schema(schema, schema_by_ref)
    if base_schema is None or schema.has_field_overrides:
        return schema.fields

    inherited_fields = _constructor_fields(base_schema, schema_by_ref, seen_refs | {schema.ref})
    inherited_names = {field.name.camel.o for field in inherited_fields}
    own_fields = tuple(
        field for field in schema.fields if field.name.camel.o not in inherited_names
    )

    return (*inherited_fields, *own_fields)


def _base_schema(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> ApiSchema | None:
    if schema.inherited_refs:
        return schema_by_ref.get(schema.inherited_refs[0])

    if schema.alias_of:
        target = schema_by_ref.get(schema.alias_of)
        if target and target.kind in {ApiSchemaKind.MODEL, ApiSchemaKind.DTO}:
            return target

    return None


def field_dependencies(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Build field dependencies for Dart emission."""
    dependencies: list[TemplateDependency] = []

    for ref in field.schema_refs:
        dependencies.append(
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=f"Field {field.name.camel.o} uses schema ref {ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    for ref in field.item_refs:
        dependencies.append(
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.ARRAY_ITEM,
                reason=f"Field {field.name.camel.o} uses array item ref {ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    return tuple(dependencies)


def dependency(
    *,
    ref: str,
    purpose: TemplateDependencyPurpose,
    reason: str,
    schema_by_ref: dict[str, ApiSchema],
    owner_ref: str | None = None,
    is_inheritance: bool = False,
) -> TemplateDependency:
    """Build a typed dependency."""
    target_schema = schema_by_ref.get(ref)
    target = _target(ref, target_schema)
    is_self = owner_ref == ref

    return TemplateDependency(
        ref=ref,
        purpose=purpose,
        reason=reason,
        target=target,
        is_inheritance=is_inheritance,
        is_self=is_self,
        is_importable=(
            not is_self
            and not target.is_primitive
            and target.kind != TemplateDependencyTargetKind.UNKNOWN
        ),
    )


def _target(ref: str, schema: ApiSchema | None) -> TemplateDependencyTarget:
    if schema is None:
        return TemplateDependencyTarget(ref=ref)

    kind = _target_kind(schema)

    return TemplateDependencyTarget(
        ref=ref,
        name=schema.name,
        kind=kind,
        schema=schema,
        is_primitive=kind == TemplateDependencyTargetKind.PRIMITIVE,
        is_enum=kind == TemplateDependencyTargetKind.ENUM,
        is_model=kind == TemplateDependencyTargetKind.MODEL,
        is_dto=kind == TemplateDependencyTargetKind.DTO,
    )


def _target_kind(schema: ApiSchema) -> TemplateDependencyTargetKind:
    kind = schema.kind.value if hasattr(schema.kind, "value") else str(schema.kind)

    if kind == "primitive":
        return TemplateDependencyTargetKind.PRIMITIVE

    if kind == "enum":
        return TemplateDependencyTargetKind.ENUM

    if kind == "model":
        return TemplateDependencyTargetKind.MODEL

    if kind == "dto":
        return TemplateDependencyTargetKind.DTO

    return TemplateDependencyTargetKind.UNKNOWN
