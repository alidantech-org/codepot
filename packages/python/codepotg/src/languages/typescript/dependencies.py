"""TypeScript dependency fact builders."""

from __future__ import annotations

from contracts.api import ApiField, ApiSchema
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
    """Build schema dependencies for TypeScript emission."""
    dependencies: list[TemplateDependency] = []

    for ref in schema.inherited_refs:
        if schema.has_field_overrides:
            parent_schema = schema_by_ref.get(ref)
            if parent_schema is not None:
                dependencies.extend(
                    _parent_field_type_dependencies(
                        schema=schema,
                        parent_schema=parent_schema,
                        schema_by_ref=schema_by_ref,
                    )
                )
            continue

        dependencies.append(
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.INHERITANCE,
                reason=f"{schema.name.pascal.o} inherits from {ref}",
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
                is_inheritance=True,
            )
        )

    for ref in schema.dependencies:
        if ref in schema.inherited_refs:
            continue

        dependencies.append(
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=f"{schema.name.pascal.o} references {ref}",
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
            )
        )

    return _unique_dependencies(tuple(dependencies))


def _parent_field_type_dependencies(
    *,
    schema: ApiSchema,
    parent_schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Import dependencies needed by flattened parent fields in override schemas."""
    dependencies: list[TemplateDependency] = []

    for ref in parent_schema.dependencies:
        if ref == parent_schema.ref:
            continue

        dependencies.append(
            dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=(
                    f"{schema.name.pascal.o} redefines fields from "
                    f"{parent_schema.name.pascal.o}, which references {ref}"
                ),
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
            )
        )

    for field in parent_schema.fields:
        for field_dependency in field_dependencies(field, schema_by_ref):
            dependencies.append(
                dependency(
                    ref=field_dependency.ref,
                    purpose=field_dependency.purpose,
                    reason=(
                        f"{schema.name.pascal.o} redefines inherited field "
                        f"{field.name.camel.o}, which uses {field_dependency.ref}"
                    ),
                    schema_by_ref=schema_by_ref,
                    owner_ref=schema.ref,
                )
            )

    return tuple(dependencies)


def field_dependencies(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Build field dependencies for TypeScript emission."""
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


def _unique_dependencies(
    dependencies: tuple[TemplateDependency, ...],
) -> tuple[TemplateDependency, ...]:
    unique: list[TemplateDependency] = []
    seen: set[tuple[str, TemplateDependencyPurpose]] = set()

    for item in dependencies:
        key = (item.ref, item.purpose)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return tuple(unique)


def dependency(
    *,
    ref: str,
    purpose: TemplateDependencyPurpose,
    reason: str,
    schema_by_ref: dict[str, ApiSchema],
    owner_ref: str | None = None,
    is_inheritance: bool = False,
) -> TemplateDependency:
    """Build a typed TypeScript dependency."""
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
        is_importable=_is_importable(target, is_self=is_self),
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


def _is_importable(
    target: TemplateDependencyTarget,
    *,
    is_self: bool,
) -> bool:
    if is_self:
        return False

    if target.is_primitive:
        return False

    return target.kind in {
        TemplateDependencyTargetKind.ENUM,
        TemplateDependencyTargetKind.MODEL,
        TemplateDependencyTargetKind.DTO,
    }
