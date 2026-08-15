from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .base import SemanticId
from .schemas import Schema, SchemaField


class SchemaResolutionError(ValueError):
    def __init__(self, code: str, message: str, *, schema: SemanticId, reference: SemanticId | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.schema = schema
        self.reference = reference


@dataclass(frozen=True, slots=True)
class EffectiveSchema:
    schema: Schema
    lineage: tuple[SemanticId, ...]
    fields: tuple[SchemaField, ...]
    field_origins: tuple[tuple[SemanticId, SemanticId], ...]

    def declared_by(self, field: SemanticId) -> SemanticId | None:
        return dict(self.field_origins).get(field)


def resolve_effective_schema(schema_id: SemanticId, schemas: Mapping[SemanticId, Schema]) -> EffectiveSchema:
    cache: dict[SemanticId, EffectiveSchema] = {}
    active: list[SemanticId] = []

    def resolve(current_id: SemanticId) -> EffectiveSchema:
        cached = cache.get(current_id)
        if cached is not None:
            return cached
        schema = schemas.get(current_id)
        if schema is None:
            raise SchemaResolutionError("IR_MISSING_BASE_SCHEMA", f"missing schema {current_id}", schema=schema_id, reference=current_id)
        if current_id in active:
            cycle = " -> ".join(str(item) for item in (*active, current_id))
            raise SchemaResolutionError("IR_SCHEMA_EXTENSION_CYCLE", f"schema extension cycle: {cycle}", schema=current_id, reference=current_id)
        active.append(current_id)
        try:
            if schema.extends is None:
                for item in schema.fields:
                    if item.overrides is not None:
                        raise SchemaResolutionError("IR_INVALID_FIELD_OVERRIDE", f"field {item.id} declares an override without a base Schema", schema=schema.id, reference=item.overrides)
                effective = EffectiveSchema(
                    schema=schema,
                    lineage=(schema.id,),
                    fields=schema.fields,
                    field_origins=tuple((item.id, schema.id) for item in schema.fields),
                )
            else:
                base = schemas.get(schema.extends)
                if base is None:
                    raise SchemaResolutionError("IR_MISSING_BASE_SCHEMA", f"schema {schema.id} extends missing schema {schema.extends}", schema=schema.id, reference=schema.extends)
                parent = resolve(base.id)
                if parent.schema.kind is not schema.kind:
                    raise SchemaResolutionError("IR_INCOMPATIBLE_SCHEMA_BASE", f"schema {schema.id} cannot extend {base.id} with different kind", schema=schema.id, reference=base.id)

                merged = list(parent.fields)
                origins = dict(parent.field_origins)
                positions_by_name = {item.name: index for index, item in enumerate(merged)}
                positions_by_id = {item.id: index for index, item in enumerate(merged)}

                for child_field in schema.fields:
                    same_name = positions_by_name.get(child_field.name)
                    if child_field.overrides is None:
                        if same_name is not None:
                            inherited = merged[same_name]
                            raise SchemaResolutionError("IR_IMPLICIT_FIELD_OVERRIDE", f"field {child_field.name} in schema {schema.id} must explicitly override inherited field {inherited.id}", schema=schema.id, reference=inherited.id)
                        positions_by_name[child_field.name] = len(merged)
                        positions_by_id[child_field.id] = len(merged)
                        merged.append(child_field)
                        origins[child_field.id] = schema.id
                        continue

                    position = positions_by_id.get(child_field.overrides)
                    if position is None:
                        raise SchemaResolutionError("IR_INVALID_FIELD_OVERRIDE", f"field {child_field.id} overrides a field that is not inherited by schema {schema.id}", schema=schema.id, reference=child_field.overrides)
                    inherited = merged[position]
                    if inherited.name != child_field.name:
                        raise SchemaResolutionError("IR_INCOMPATIBLE_FIELD_OVERRIDE", f"field {child_field.id} must preserve inherited field name {inherited.name}", schema=schema.id, reference=inherited.id)
                    if inherited.type != child_field.type:
                        raise SchemaResolutionError("IR_INCOMPATIBLE_FIELD_OVERRIDE", f"field {child_field.name} changes inherited type in schema {schema.id}", schema=schema.id, reference=inherited.id)
                    if same_name is not None and same_name != position:
                        raise SchemaResolutionError("IR_INCOMPATIBLE_FIELD_OVERRIDE", f"field {child_field.name} conflicts with another inherited field", schema=schema.id, reference=inherited.id)
                    origins.pop(inherited.id, None)
                    merged[position] = child_field
                    positions_by_id.pop(inherited.id, None)
                    positions_by_id[child_field.id] = position
                    origins[child_field.id] = schema.id

                effective = EffectiveSchema(
                    schema=schema,
                    lineage=(*parent.lineage, schema.id),
                    fields=tuple(merged),
                    field_origins=tuple((item.id, origins[item.id]) for item in merged),
                )
            cache[current_id] = effective
            return effective
        finally:
            active.pop()

    return resolve(schema_id)


__all__ = ["EffectiveSchema", "SchemaResolutionError", "resolve_effective_schema"]
