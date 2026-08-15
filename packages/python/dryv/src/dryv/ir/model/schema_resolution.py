from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

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
                effective = EffectiveSchema(schema=schema, lineage=(schema.id,), fields=schema.fields)
            else:
                base = schemas.get(schema.extends)
                if base is None:
                    raise SchemaResolutionError("IR_MISSING_BASE_SCHEMA", f"schema {schema.id} extends missing schema {schema.extends}", schema=schema.id, reference=schema.extends)
                parent = resolve(base.id)
                if parent.schema.kind is not schema.kind:
                    raise SchemaResolutionError("IR_INCOMPATIBLE_SCHEMA_BASE", f"schema {schema.id} cannot extend {base.id} with different kind", schema=schema.id, reference=base.id)
                merged = list(parent.fields)
                positions = {item.name: index for index, item in enumerate(merged)}
                for child_field in schema.fields:
                    position = positions.get(child_field.name)
                    if position is None:
                        positions[child_field.name] = len(merged)
                        merged.append(child_field)
                        continue
                    inherited = merged[position]
                    if inherited.type != child_field.type:
                        raise SchemaResolutionError("IR_INCOMPATIBLE_FIELD_OVERRIDE", f"field {child_field.name} changes inherited type in schema {schema.id}", schema=schema.id, reference=inherited.id)
                    merged[position] = child_field
                effective = EffectiveSchema(schema=schema, lineage=(*parent.lineage, schema.id), fields=tuple(merged))
            cache[current_id] = effective
            return effective
        finally:
            active.pop()

    return resolve(schema_id)


__all__ = ["EffectiveSchema", "SchemaResolutionError", "resolve_effective_schema"]
