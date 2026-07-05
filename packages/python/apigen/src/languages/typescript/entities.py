"""TypeScript entity template builders."""

from __future__ import annotations

import json

from contracts.api import ApiEntity, ApiEntityField, ApiFieldKind, ApiSchema
from contracts.names import make_contract_name
from contracts.template import (
    TemplateDocs,
    TemplateEntity,
    TemplateEntityConstraint,
    TemplateEntityField,
    TemplateEntityFieldMeta,
    TemplateEntityMeta,
    TemplateEntityRelation,
    TemplateFieldLang,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
    TemplateOperationResource,
)
from languages.debug.context.path_values import safe_file_name
from languages.typescript.names import name_text


def template_entities(
    entities: tuple[ApiEntity, ...],
    *,
    resource_paths: dict[str, tuple[str, ...]],
    resources_by_id: dict[str, object],
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateEntity, ...]:
    """Build TypeScript entity template variables."""
    return tuple(
        _entity(
            entity,
            resource_paths=resource_paths,
            resources_by_id=resources_by_id,
            schema_by_ref=schema_by_ref,
            entities=entities,
        )
        for entity in entities
    )


def entities_for_resource(
    entities: tuple[TemplateEntity, ...],
    resource_path: tuple[str, ...],
) -> tuple[TemplateEntity, ...]:
    """Return entities belonging to a resource path."""
    return tuple(entity for entity in entities if entity.meta.resource_path == resource_path)


def _entity(
    entity: ApiEntity,
    *,
    resource_paths: dict[str, tuple[str, ...]],
    resources_by_id: dict[str, object],
    schema_by_ref: dict[str, ApiSchema],
    entities: tuple[ApiEntity, ...],
) -> TemplateEntity:
    resource_path = resource_paths.get(entity.resource or "", ("shared",))
    resource = _entity_resource(entity, resource_path, resources_by_id)
    schema = schema_by_ref.get(entity.schema_ref or "")
    class_name = f"{entity.name.pascal.o}Entity"
    file_name = f"{safe_file_name(name_text(entity.name.kebab.o), fallback=entity.id)}.entity"

    return TemplateEntity(
        api=entity,
        name=entity.name,
        resource=resource,
        fields=tuple(_field(field, schema_by_ref) for field in entity.fields),
        backend_fields=tuple(_field(field, schema_by_ref) for field in entity.backend_fields),
        relations=tuple(_relation(relation, entity, entities) for relation in entity.relations),
        constraints=tuple(
            TemplateEntityConstraint(
                api=constraint,
                name=constraint.name,
                kind=constraint.kind,
                fields=constraint.fields,
                unique=constraint.kind == "unique",
                meta=constraint.meta,
            )
            for constraint in entity.constraints
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.RESOURCES,
            item_key=TemplateItemKey.ENTITY,
            key=entity.id,
            ref=None,
            path_parts=("entities", entity.name.path.o),
            resource_path=resource_path,
            folder_path=(*resource_path, "entities"),
            file_name=file_name,
            relative_doc_path=(*resource_path, "entities", f"{file_name}.ts"),
        ),
        docs=TemplateDocs(),
        meta=TemplateEntityMeta(
            resource_path=resource_path,
            resource_name=resource.name if resource is not None else None,
            schema_type=schema.name.pascal.o if schema is not None else None,
            store=entity.store,
            table_name=entity.store,
            base_class=_base_class(entity),
            interface_type=schema.name.pascal.o if schema is not None else None,
            class_name=class_name,
            file_name=file_name,
            raw=entity.meta.get("x-codegen", {}),
        ),
    )


def _entity_resource(
    entity: ApiEntity,
    resource_path: tuple[str, ...],
    resources_by_id: dict[str, object],
) -> TemplateOperationResource | None:
    if entity.resource is None:
        return None
    resource = resources_by_id.get(entity.resource)
    name = getattr(resource, "name", make_contract_name(entity.resource))
    raw = getattr(resource, "meta", {}).get("x-codegen", {}) if resource is not None else {}
    return TemplateOperationResource(
        name=name,
        path=getattr(resource, "path", ()) if resource is not None else (),
        route=str(raw.get("route")) if isinstance(raw, dict) and raw.get("route") else None,
    )


def _field(
    field: ApiEntityField,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateEntityField:
    schema = schema_by_ref.get(field.schema_ref or "")
    enum_type = schema.name.pascal.o if schema is not None and schema.kind.value == "enum" else None
    raw = field.meta.get("x-codegen", {})
    return TemplateEntityField(
        api=field,
        name=field.name,
        lang=TemplateFieldLang(
            kind="typescript_entity_field",
            type=_field_type(field, schema_by_ref),
            display_name=field.name.camel.o,
            nullable=field.nullable,
            required=field.required,
        ),
        meta=TemplateEntityFieldMeta(
            column_name=field.name.snake.o,
            column_type=_column_type(field, enum_type),
            enum_type=enum_type,
            nullable=field.nullable,
            primary=bool(isinstance(raw, dict) and raw.get("role") == "primaryKey"),
            generated=(
                str(raw.get("generated"))
                if isinstance(raw, dict) and raw.get("generated")
                else None
            ),
            default=field.default,
            min_length=field.min_length,
            max_length=field.max_length,
            minimum=field.minimum,
            maximum=field.maximum,
            exclusive_minimum=field.exclusive_minimum,
            exclusive_maximum=field.exclusive_maximum,
            multiple_of=field.multiple_of,
            pattern=field.pattern,
            column_options=_column_options(field, enum_type),
            backend_only=bool(field.meta.get("backend_only")),
            raw=raw if isinstance(raw, dict) else {},
        ),
    )


def _field_type(field: ApiEntityField, schema_by_ref: dict[str, ApiSchema]) -> str:
    schema = schema_by_ref.get(field.schema_ref or "")
    if schema is not None and schema.kind.value != "primitive":
        base = f"ApiTypes.{schema.name.pascal.o}"
    else:
        primitive_type = schema.primitive_type if schema is not None else field.type.type
        primitive_format = (
            schema.primitive_format if schema is not None else field.type.resolved_format
        )
        kind = field.type.kind
        if kind == ApiFieldKind.ARRAY:
            base = "unknown[]"
        elif primitive_format == "date-time":
            base = "Date"
        elif primitive_type in {"integer", "number"}:
            base = "number"
        elif primitive_type == "boolean":
            base = "boolean"
        else:
            base = "string"
    return f"{base} | null" if field.nullable else base


def _column_type(field: ApiEntityField, enum_type: str | None) -> str:
    if enum_type:
        return "simple-enum"
    if field.type.resolved_format == "uuid" or field.name.camel.o.endswith("Id"):
        return "uuid"
    if field.type.resolved_format == "date-time":
        return "timestamptz"
    if field.type.type == "boolean":
        return "boolean"
    if field.type.type == "integer":
        return "int"
    if field.type.type == "number":
        return "numeric"
    if field.max_length is not None and field.max_length > 255:
        return "text"
    if field.name.camel.o.lower().endswith(("description", "text", "metadata")):
        return "text"
    return "varchar"


def _column_options(field: ApiEntityField, enum_type: str | None) -> str:
    column_type = _column_type(field, enum_type)
    options = [
        f"type: '{column_type}'",
        f"name: '{field.name.snake.o}'",
    ]
    if enum_type:
        options.append(f"enum: ApiTypes.{enum_type}")
    if column_type == "varchar" and field.max_length is not None:
        options.append(f"length: {field.max_length}")
    options.append(f"nullable: {_ts_bool(field.nullable)}")
    if field.default is not None:
        options.append(f"default: {_ts_literal(field.default)}")
    if field.minimum is not None or field.maximum is not None:
        options.append(f"comment: {_ts_literal(_range_comment(field))}")
    return ", ".join(options)


def _range_comment(field: ApiEntityField) -> str:
    parts = []
    if field.minimum is not None:
        parts.append(f"minimum={field.minimum}")
    if field.maximum is not None:
        parts.append(f"maximum={field.maximum}")
    if field.exclusive_minimum is not None:
        parts.append(f"exclusiveMinimum={field.exclusive_minimum}")
    if field.exclusive_maximum is not None:
        parts.append(f"exclusiveMaximum={field.exclusive_maximum}")
    if field.multiple_of is not None:
        parts.append(f"multipleOf={field.multiple_of}")
    if field.pattern is not None:
        parts.append(f"pattern={field.pattern}")
    return "OpenAPI constraints: " + ", ".join(parts)


def _ts_literal(value: object) -> str:
    return json.dumps(value)


def _ts_bool(value: bool) -> str:
    return "true" if value else "false"


def _relation(
    relation,
    source_entity: ApiEntity,
    entities: tuple[ApiEntity, ...],
) -> TemplateEntityRelation:
    target = _target_entity(relation.target_ref, entities)
    inverse = _inverse_relation_name(relation, source_entity, target)
    return TemplateEntityRelation(
        api=relation,
        name=relation.name,
        target_entity_name=target.name.pascal.o if target is not None else None,
        target_class_name=f"{target.name.pascal.o}Entity" if target is not None else None,
        target_file_name=(
            f"{safe_file_name(name_text(target.name.kebab.o), fallback=target.id)}.entity"
            if target is not None
            else None
        ),
        inverse_field_name=inverse,
        meta=relation.meta,
    )


def _inverse_relation_name(
    relation,
    source_entity: ApiEntity,
    target: ApiEntity | None,
) -> str | None:
    if target is None:
        return None

    if relation.cardinality in {"belongsTo", "hasOne"}:
        source_ref = f"#/x-codegen/entities/{source_entity.resource}/{source_entity.name.pascal.o}"
        for target_relation in target.relations:
            if target_relation.target_ref == source_ref:
                return target_relation.name.camel.o

    if relation.foreign and relation.foreign.endswith("Id"):
        return relation.foreign[:-2]

    return None


def _target_entity(target_ref: str | None, entities: tuple[ApiEntity, ...]) -> ApiEntity | None:
    if not target_ref:
        return None
    target_name = target_ref.rsplit("/", 1)[-1]
    for entity in entities:
        if entity.name.pascal.o == target_name or entity.id.endswith(f".{target_name}"):
            return entity
    return None


def _base_class(entity: ApiEntity) -> str | None:
    key = entity.extends.get("key")
    return f"{key}Entity" if isinstance(key, str) and key else None
