"""Schema inference layer.

This package provides utilities for inferring schema structure including
fields, aliases, enums, composition, and metadata from OpenAPI schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from constants.codegen import X_CODEGEN
from constants.openapi import REF_SCHEMAS
from inference.classifiers import classify_schema
from inference.metadata.query import infer_query_metadata
from inference.models import InferredResource, InferredSchema, InferredSchemaKind
from inference.models.schemas import InferredSchemaComposition, InferredSchemaField, QueryMetadata
from inference.resources import extract_resource_from_x_codegen
from inference.schemas.composition import (
    get_composition_refs,
    get_inherited_refs,
    infer_composition,
    split_nullable_union,
)
from inference.schemas.enums import infer_enum_type, infer_enum_values
from inference.schemas.fields import infer_schema_fields
from inference.schemas.primitives import infer_primitive_format, infer_primitive_type
from inference.schemas.resolution import resolve_schema_alias
from openapi.document import OpenApiDocument
from openapi.refs import find_refs, get_ref


def infer_schemas(document: OpenApiDocument) -> tuple[InferredSchema, ...]:
    schemas: list[InferredSchema] = []

    for name, schema in document.schemas.items():
        if not isinstance(schema, dict):
            continue

        ref = f"{REF_SCHEMAS}{name}"
        x_codegen = schema.get(X_CODEGEN)
        x_codegen_dict = x_codegen if isinstance(x_codegen, dict) else {}

        alias_info = _detect_alias(schema)
        is_alias = alias_info is not None
        alias_of = alias_info if is_alias else None

        # Detect nullable union and extract effective schema
        effective_schema, nullable = split_nullable_union(schema)

        kind_fields = _infer_kind_specific_fields(
            effective_schema,
            classify_schema(str(name), effective_schema, document=document),
            document,
            nullable,
            schema,
        )
        schemas.append(
            InferredSchema(
                name=str(name),
                ref=ref,
                kind=classify_schema(str(name), effective_schema, document=document),
                resource=extract_resource_from_x_codegen(x_codegen_dict, document)
                or _infer_resource_from_alias(effective_schema, document),
                x_codegen=x_codegen_dict,
                raw=schema,
                dependencies=_dedupe_dependencies(
                    found_ref.raw
                    for found_ref in find_refs(schema)
                    if found_ref.raw != f"{REF_SCHEMAS}{name}"
                ),
                alias_of=alias_of,
                is_alias=is_alias,
                nullable=nullable,
                primitive_type=kind_fields.primitive_type,
                primitive_format=kind_fields.primitive_format,
                query=kind_fields.query,
                enum_type=kind_fields.enum_type,
                enum_values=kind_fields.enum_values,
                fields=kind_fields.fields,
                composition_refs=kind_fields.composition_refs,
                inherited_refs=kind_fields.inherited_refs,
                composition=kind_fields.composition,
            )
        )

    return _resolve_field_query_metadata(tuple(schemas))


def _infer_resource_from_alias(
    schema: dict[str, Any],
    document: OpenApiDocument,
) -> InferredResource | None:
    from inference.ref_metadata import infer_resource_from_ref_alias

    return infer_resource_from_ref_alias(schema, document)


def _detect_alias(schema: dict[str, Any]) -> str | None:
    ref = get_ref(schema)
    if ref is not None and ref.is_component:
        return ref.raw
    return None


def _dedupe_dependencies(dependencies: Any) -> tuple[str, ...]:
    """Deduplicate dependency refs while preserving order.

    Args:
        dependencies: An iterable of dependency refs.

    Returns:
        A tuple of unique dependency refs in order of first appearance.
    """
    seen: set[str] = set()
    result: list[str] = []

    for dep in dependencies:
        if dep not in seen:
            seen.add(dep)
            result.append(dep)

    return tuple(result)


@dataclass(frozen=True)
class KindSpecificFields:
    """Kind-specific fields for inferred schemas."""

    primitive_type: str | None = None
    primitive_format: str | None = None
    query: QueryMetadata = field(default_factory=QueryMetadata)
    enum_type: str | None = None
    enum_values: tuple[str, ...] | None = None
    fields: tuple[InferredSchemaField, ...] = ()
    composition_refs: tuple[str, ...] = ()
    inherited_refs: tuple[str, ...] = ()
    composition: InferredSchemaComposition | None = None


def _infer_kind_specific_fields(
    schema: dict[str, Any],
    kind: InferredSchemaKind,
    document: OpenApiDocument,
    nullable: bool = False,
    original_schema: dict[str, Any] | None = None,
) -> KindSpecificFields:
    """Infer kind-specific fields based on schema kind.

    Args:
        schema: An OpenAPI schema object.
        kind: The inferred schema kind.
        document: The OpenAPI document for alias resolution.
        nullable: Whether the schema is nullable.
        original_schema: The original schema before nullable union extraction (for required fields).

    Returns:
        A KindSpecificFields object with kind-specific fields.
    """
    # Resolve effective schema for type/format/enum/field details
    effective_schema = resolve_schema_alias(document, schema) or schema

    # Use original schema for required field extraction if provided
    schema_for_fields = original_schema if original_schema is not None else effective_schema

    if kind == InferredSchemaKind.PRIMITIVE:
        return KindSpecificFields(
            primitive_type=infer_primitive_type(effective_schema),
            primitive_format=infer_primitive_format(effective_schema),
            query=infer_query_metadata(effective_schema),
            fields=(),
            composition_refs=(),
            inherited_refs=(),
            composition=None,
        )

    if kind == InferredSchemaKind.ENUM:
        return KindSpecificFields(
            query=infer_query_metadata(effective_schema),
            enum_type=infer_enum_type(effective_schema),
            enum_values=infer_enum_values(effective_schema),
            fields=(),
            composition_refs=(),
            inherited_refs=(),
            composition=None,
        )

    if kind in (InferredSchemaKind.MODEL, InferredSchemaKind.DTO):
        return KindSpecificFields(
            fields=infer_schema_fields(schema_for_fields, document),
            composition_refs=get_composition_refs(effective_schema),
            inherited_refs=get_inherited_refs(effective_schema),
            composition=infer_composition(effective_schema),
        )

    # UNKNOWN or other kinds
    return KindSpecificFields(
        fields=(),
        composition_refs=(),
        inherited_refs=(),
        composition=None,
    )


def _resolve_field_query_metadata(
    schemas: tuple[InferredSchema, ...],
) -> tuple[InferredSchema, ...]:
    """Inherit field query metadata from referenced schemas when direct metadata is empty."""
    schema_by_ref = {schema.ref: schema for schema in schemas}
    resolved: list[InferredSchema] = []

    for schema in schemas:
        if not schema.fields:
            resolved.append(schema)
            continue

        fields = tuple(_resolve_single_field_query(field, schema_by_ref) for field in schema.fields)
        resolved.append(replace(schema, fields=fields))

    return tuple(resolved)


def _resolve_single_field_query(
    field: InferredSchemaField,
    schema_by_ref: dict[str, InferredSchema],
) -> InferredSchemaField:
    """Resolve query metadata for one field."""
    if field.query.enabled:
        return field

    inherited = _query_from_refs(
        refs=(
            field.schema_ref,
            *field.schema_refs,
            field.item_ref,
            *field.item_refs,
        ),
        schema_by_ref=schema_by_ref,
    )

    if not inherited.enabled:
        return field

    return replace(field, query=inherited)


def _query_from_refs(
    *,
    refs: tuple[str | None, ...],
    schema_by_ref: dict[str, InferredSchema],
) -> QueryMetadata:
    for ref in refs:
        if not ref:
            continue

        schema = schema_by_ref.get(ref)
        if schema is not None and schema.query.enabled:
            return schema.query

    return QueryMetadata()


__all__ = ["infer_schemas"]
