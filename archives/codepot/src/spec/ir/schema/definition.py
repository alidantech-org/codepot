"""Root schema registry models for compiled Codepot IR."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from archives.codepot.src.spec.ir.schema.dto.definition import DtoDefinition
from archives.codepot.src.spec.ir.schema.entity.definition import EntityDefinition
from archives.codepot.src.spec.ir.schema.entity.field.definition import EntityFieldDefinition
from archives.codepot.src.spec.ir.schema.field_set.definition import FieldSetDefinition
from archives.codepot.src.spec.ir.schema.model.definition import ModelDefinition
from archives.codepot.src.spec.ir.schema.params.definition import ParamsDefinition

RefSchema = (
    EntityDefinition
    | EntityFieldDefinition
    | FieldSetDefinition
    | ModelDefinition
    | DtoDefinition
)


class SchemasDefinition(BaseModel):
    """Compiled reusable schema registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entities: dict[str, EntityDefinition]
    field_sets: dict[str, FieldSetDefinition]
    models: dict[str, ModelDefinition]
    dtos: dict[str, DtoDefinition]
    params: dict[str, ParamsDefinition]
