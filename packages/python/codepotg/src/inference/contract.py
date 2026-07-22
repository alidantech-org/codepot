"""Inference-to-API contract mapping.

This module converts existing inference facts into stable API contract models.
It must not infer from raw OpenAPI, classify raw schemas, or parse x-codegen.
"""

from __future__ import annotations

from typing import Any

from constants.codegen import (
    KIND_DTO,
    KIND_ENUM,
    KIND_MODEL,
    KIND_PRIMITIVE,
    UI,
    X_CODEGEN,
)
from constants.http import (
    DELETE,
    GET,
    HEAD,
    OPTIONS,
    PATCH,
    POST,
    PUT,
    TRACE,
)
from constants.openapi import (
    DESCRIPTION,
    RAW,
    SUMMARY,
    TYPE_ARRAY,
    TYPE_OBJECT,
    URL,
    VARIABLES,
)
from contracts.api import (
    ApiComposition,
    ApiContract,
    ApiDependency,
    ApiDocumentInfo,
    ApiEntity,
    ApiEntityConstraint,
    ApiEntityField,
    ApiEntityRelation,
    ApiEnumValue,
    ApiField,
    ApiFieldKind,
    ApiFieldType,
    ApiHttpMethod,
    ApiMediaType,
    ApiOperation,
    ApiOperationTarget,
    ApiParameter,
    ApiQueryOptions,
    ApiRequestBody,
    ApiResource,
    ApiResponse,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
    ApiServer,
)
from contracts.names import make_contract_name
from inference.models import (
    InferenceGraph,
    InferredDependency,
    InferredMediaType,
    InferredOperation,
    InferredOperationTarget,
    InferredParameter,
    InferredRequestBody,
    InferredResource,
    InferredResponse,
    InferredSchema,
    InferredSchemaKind,
)
from inference.models.schemas import (
    InferredSchemaComposition,
    InferredSchemaField,
    QueryMetadata,
)


def _map_schema_kind(kind: InferredSchemaKind) -> ApiSchemaKind:
    """Map inference schema kind to API schema kind enum."""
    kind_map = {
        InferredSchemaKind.MODEL: ApiSchemaKind.MODEL,
        InferredSchemaKind.DTO: ApiSchemaKind.DTO,
        InferredSchemaKind.ENUM: ApiSchemaKind.ENUM,
        InferredSchemaKind.PRIMITIVE: ApiSchemaKind.PRIMITIVE,
        InferredSchemaKind.UNKNOWN: ApiSchemaKind.UNKNOWN,
    }
    return kind_map.get(kind, ApiSchemaKind.UNKNOWN)


def _map_field_kind(kind: str | None) -> ApiFieldKind:
    """Map inference field kind string to API field kind enum."""
    if not kind:
        return ApiFieldKind.UNKNOWN

    kind_map = {
        KIND_PRIMITIVE: ApiFieldKind.PRIMITIVE,
        KIND_ENUM: ApiFieldKind.ENUM,
        KIND_MODEL: ApiFieldKind.MODEL,
        KIND_DTO: ApiFieldKind.DTO,
        TYPE_ARRAY: ApiFieldKind.ARRAY,
        TYPE_OBJECT: ApiFieldKind.OBJECT,
    }
    return kind_map.get(kind.lower(), ApiFieldKind.UNKNOWN)


def _map_http_method(method: str) -> ApiHttpMethod:
    """Map HTTP method string to API HTTP method enum."""
    method_map = {
        GET: ApiHttpMethod.GET,
        POST: ApiHttpMethod.POST,
        PUT: ApiHttpMethod.PUT,
        PATCH: ApiHttpMethod.PATCH,
        DELETE: ApiHttpMethod.DELETE,
        OPTIONS: ApiHttpMethod.OPTIONS,
        HEAD: ApiHttpMethod.HEAD,
        TRACE: ApiHttpMethod.TRACE,
    }
    return method_map.get(method.lower(), ApiHttpMethod.UNKNOWN)


def build_api_contract(graph: InferenceGraph) -> ApiContract:
    """Build a stable API contract from an inference graph."""
    schemas = tuple(_schema(schema, graph.schemas) for schema in graph.schemas)

    return ApiContract(
        info=ApiDocumentInfo(
            title=graph.title,
            openapi_version=graph.openapi_version,
            api_version=graph.api_version,
            description=graph.description,
        ),
        resources=tuple(_resource(resource, graph) for resource in graph.resources),
        servers=tuple(_server(server) for server in graph.servers),
        schemas=_schema_groups(schemas),
        operations=tuple(_operation(operation) for operation in graph.operations),
        entities=_entities(graph.x_codegen or {}, schemas),
        dependencies=tuple(_dependency(dependency) for dependency in graph.dependencies),
        meta={
            X_CODEGEN: graph.x_codegen or {},
        },
    )


def _server(server: dict[str, Any]) -> ApiServer:
    url = server.get(URL)
    description = server.get(DESCRIPTION)
    variables = server.get(VARIABLES)

    return ApiServer(
        url=url.strip() if isinstance(url, str) else "",
        description=(
            description.strip() if isinstance(description, str) and description.strip() else "-"
        ),
        variables=variables if isinstance(variables, dict) else {},
        meta={RAW: server},
    )


def _resource(resource: InferredResource, graph: InferenceGraph) -> ApiResource:
    operations_count = sum(1 for operation in graph.operations if operation.resource == resource)

    return ApiResource(
        id=resource.name,
        name=make_contract_name(resource.name),
        path=resource.path,
        path_name=make_contract_name("_".join(resource.path) if resource.path else resource.name),
        operations_count=operations_count,
        meta={
            X_CODEGEN: _resource_x_codegen(resource, graph.x_codegen or {}),
        },
    )


def _detect_field_overrides(
    schema: InferredSchema,
    schema_by_ref: dict[str, InferredSchema],
) -> bool:
    """Detect if schema overrides any inherited fields."""
    if not schema.inherited_refs:
        return False

    # Get base schema fields by wire name
    base_fields_by_wire = {}
    for ref in schema.inherited_refs:
        base_schema = schema_by_ref.get(ref)
        if base_schema:
            for field in base_schema.fields:
                base_fields_by_wire[field.name] = field

    # Check for overrides
    own_fields_by_wire = {field.name: field for field in schema.fields}
    overridden_names = set(base_fields_by_wire) & set(own_fields_by_wire)

    return bool(overridden_names)


def _schema(schema: InferredSchema, schemas: tuple[InferredSchema, ...]) -> ApiSchema:
    schema_by_ref = {s.ref: s for s in schemas}
    has_field_overrides = _detect_field_overrides(schema, schema_by_ref)

    # For root $ref aliases to object-like schemas, copy fields from target
    fields = tuple(_field(field, schemas) for field in _tuple(schema.fields))
    if schema.is_alias and schema.alias_of:
        target = schema_by_ref.get(schema.alias_of)
        if target and target.kind in {InferredSchemaKind.MODEL, InferredSchemaKind.DTO}:
            fields = tuple(_field(field, schemas) for field in _tuple(target.fields))

    return ApiSchema(
        id=schema.name,
        name=make_contract_name(schema.name),
        ref=schema.ref,
        kind=_map_schema_kind(schema.kind),
        resource=_resource_name(schema.resource),
        dependencies=_tuple(schema.dependencies),
        is_alias=schema.is_alias,
        alias_of=schema.alias_of,
        nullable=schema.nullable,
        primitive_type=schema.primitive_type,
        primitive_format=schema.primitive_format,
        query=_query(schema.query),
        enum_type=schema.enum_type,
        enum_values=tuple(_enum_value(value) for value in _tuple(schema.enum_values)),
        fields=fields,
        composition_refs=_tuple(schema.composition_refs),
        inherited_refs=_tuple(schema.inherited_refs),
        composition=_composition(schema.composition),
        has_field_overrides=has_field_overrides,
        description=str(schema.raw.get(DESCRIPTION) or "-"),
        meta={
            X_CODEGEN: schema.x_codegen,
        },
    )


def _field(field: InferredSchemaField, schemas: tuple[InferredSchema, ...]) -> ApiField:
    nullable = field.nullable

    # Inherit nullable from referenced schema if not already nullable
    if not nullable and field.schema_ref:
        schema_by_ref = {s.ref: s for s in schemas}
        ref_schema = schema_by_ref.get(field.schema_ref)
        if ref_schema and ref_schema.nullable:
            nullable = True

    return ApiField(
        id=field.name,
        name=make_contract_name(field.name),
        required=field.required,
        nullable=nullable,
        type=ApiFieldType(
            raw_type=field.raw_type,
            format=field.format,
            kind=_map_field_kind(field.resolved_kind),
            type=field.resolved_type,
            resolved_format=field.resolved_format,
            item_kind=_map_field_kind(field.resolved_item_kind),
            item_type=field.resolved_item_type,
            item_format=field.resolved_item_format,
        ),
        schema_ref=field.schema_ref,
        schema_refs=_tuple(field.schema_refs),
        item_ref=field.item_ref,
        item_refs=_tuple(field.item_refs),
        enum_values=tuple(str(value) for value in _tuple(field.enum_values)),
        default=field.default,
        min_length=field.min_length,
        max_length=field.max_length,
        minimum=field.minimum,
        maximum=field.maximum,
        exclusive_minimum=field.exclusive_minimum,
        exclusive_maximum=field.exclusive_maximum,
        multiple_of=field.multiple_of,
        pattern=field.pattern,
        description=field.description or "-",
        query=_query(field.query),
    )


def _enum_value(value: str) -> ApiEnumValue:
    return ApiEnumValue(
        value=value,
        name=make_contract_name(value),
    )


def _composition(
    composition: InferredSchemaComposition | None,
) -> ApiComposition | None:
    if composition is None:
        return None

    return ApiComposition(
        kind=composition.kind,
        refs=composition.refs,
        inline_field_count=composition.inline_field_count,
    )


def _operation(operation: InferredOperation) -> ApiOperation:
    x_codegen = operation.raw.get(X_CODEGEN)
    x_codegen = x_codegen if isinstance(x_codegen, dict) else {}
    return ApiOperation(
        id=operation.operation_id,
        name=make_contract_name(operation.operation_id),
        method=_map_http_method(operation.method),
        path=operation.path,
        resource=_resource_name(operation.resource),
        parameters=tuple(_parameter(parameter) for parameter in operation.parameters),
        request_body=_request_body(operation.request_body),
        responses=tuple(_response(response) for response in operation.responses),
        target=_operation_target(operation.target),
        description=str(operation.raw.get(DESCRIPTION) or operation.raw.get(SUMMARY) or "-"),
        meta={
            UI: operation.ui,
            X_CODEGEN: x_codegen,
        },
    )


def _entities(x_codegen: dict[str, Any], schemas: tuple[ApiSchema, ...]) -> tuple[ApiEntity, ...]:
    raw_entities = x_codegen.get("entities")
    if not isinstance(raw_entities, dict):
        return ()

    schema_by_ref = {schema.ref: schema for schema in schemas}
    entities: list[ApiEntity] = []
    for resource_key, resource_entities in raw_entities.items():
        if not isinstance(resource_entities, dict):
            continue
        for entity_name, raw_entity in resource_entities.items():
            if not isinstance(raw_entity, dict):
                continue
            entities.append(
                _entity(
                    resource_key=str(resource_key),
                    entity_name=str(entity_name),
                    raw=raw_entity,
                    schema_by_ref=schema_by_ref,
                )
            )
    return tuple(entities)


def _entity(
    *,
    resource_key: str,
    entity_name: str,
    raw: dict[str, Any],
    schema_by_ref: dict[str, ApiSchema],
) -> ApiEntity:
    schema_ref = _ref(raw.get("schema"))
    schema = schema_by_ref.get(schema_ref or "")
    field_meta = raw.get("fields") if isinstance(raw.get("fields"), dict) else {}
    backend_meta = raw.get("backend") if isinstance(raw.get("backend"), dict) else {}

    return ApiEntity(
        id=f"{resource_key}.{entity_name}",
        name=make_contract_name(entity_name),
        resource=resource_key,
        resource_ref=_ref(raw.get("resource")),
        schema_ref=schema_ref,
        store=str(raw.get("store")) if raw.get("store") is not None else None,
        extends=raw.get("extends") if isinstance(raw.get("extends"), dict) else {},
        fields=tuple(
            _entity_field(field.id, field_meta.get(field.id), field)
            for field in (schema.fields if schema is not None else ())
        ),
        backend_fields=tuple(
            _entity_backend_field(name, value) for name, value in backend_meta.items()
        ),
        relations=tuple(
            _entity_relation(name, value)
            for name, value in _dict(raw.get("relations")).items()
        ),
        constraints=tuple(
            _entity_constraint(name, value)
            for name, value in _dict(raw.get("constraints")).items()
        ),
        meta={
            X_CODEGEN: raw,
        },
    )


def _entity_field(name: str, raw: Any, schema_field: ApiField) -> ApiEntityField:
    raw = raw if isinstance(raw, dict) else {}
    return ApiEntityField(
        id=name,
        name=make_contract_name(name),
        schema_ref=schema_field.schema_ref,
        required=schema_field.required,
        nullable=schema_field.nullable,
        type=schema_field.type,
        default=raw.get("default", schema_field.default),
        min_length=_int_meta(raw, "minLength", schema_field.min_length),
        max_length=_int_meta(raw, "maxLength", schema_field.max_length),
        minimum=_number_meta(raw, "minimum", schema_field.minimum),
        maximum=_number_meta(raw, "maximum", schema_field.maximum),
        exclusive_minimum=raw.get("exclusiveMinimum", schema_field.exclusive_minimum),
        exclusive_maximum=raw.get("exclusiveMaximum", schema_field.exclusive_maximum),
        multiple_of=_number_meta(raw, "multipleOf", schema_field.multiple_of),
        pattern=_string_meta(raw, "pattern", schema_field.pattern),
        meta={
            X_CODEGEN: raw,
            "schema_field": schema_field,
        },
    )


def _entity_backend_field(name: str, raw: Any) -> ApiEntityField:
    raw_dict = raw if isinstance(raw, dict) else {}
    return ApiEntityField(
        id=name,
        name=make_contract_name(name),
        schema_ref=_ref(raw_dict),
        required=True,
        nullable=False,
        default=raw_dict.get("default"),
        min_length=_int_meta(raw_dict, "minLength", None),
        max_length=_int_meta(raw_dict, "maxLength", None),
        minimum=_number_meta(raw_dict, "minimum", None),
        maximum=_number_meta(raw_dict, "maximum", None),
        exclusive_minimum=raw_dict.get("exclusiveMinimum"),
        exclusive_maximum=raw_dict.get("exclusiveMaximum"),
        multiple_of=_number_meta(raw_dict, "multipleOf", None),
        pattern=_string_meta(raw_dict, "pattern", None),
        meta={
            X_CODEGEN: raw_dict,
            "backend_only": True,
        },
    )


def _entity_relation(name: str, raw: Any) -> ApiEntityRelation:
    raw = raw if isinstance(raw, dict) else {}
    return ApiEntityRelation(
        id=name,
        name=make_contract_name(name),
        cardinality=str(raw.get("cardinality") or "-"),
        target_ref=_ref(raw.get("target")),
        local=str(raw.get("local")) if raw.get("local") is not None else None,
        foreign=str(raw.get("foreign")) if raw.get("foreign") is not None else None,
        meta={X_CODEGEN: raw},
    )


def _entity_constraint(name: str, raw: Any) -> ApiEntityConstraint:
    raw = raw if isinstance(raw, dict) else {}
    fields = raw.get("fields")
    return ApiEntityConstraint(
        id=name,
        name=make_contract_name(name),
        kind=str(raw.get("kind") or "-"),
        fields=tuple(str(field) for field in fields) if isinstance(fields, list | tuple) else (),
        meta={X_CODEGEN: raw},
    )


def _parameter(parameter: InferredParameter) -> ApiParameter:
    return ApiParameter(
        id=parameter.name,
        name=make_contract_name(parameter.name),
        location=parameter.location,
        required=parameter.required,
        ref=parameter.ref,
        schema_ref=parameter.schema_ref,
        schema_refs=parameter.schema_refs,
    )


def _request_body(
    request_body: InferredRequestBody | None,
) -> ApiRequestBody | None:
    if request_body is None:
        return None

    return ApiRequestBody(
        ref=request_body.ref,
        required=request_body.required,
        content_types=tuple(str(value) for value in _tuple(request_body.content_types)),
        media_types=tuple(
            _media_type(media_type) for media_type in _tuple(request_body.media_types)
        ),
        schema_refs=tuple(str(value) for value in _tuple(request_body.schema_refs)),
    )


def _response(response: InferredResponse) -> ApiResponse:
    return ApiResponse(
        status_code=response.status_code,
        ref=response.ref,
        description=response.description or "-",
        content_types=tuple(str(value) for value in _tuple(response.content_types)),
        media_types=tuple(_media_type(media_type) for media_type in _tuple(response.media_types)),
        schema_refs=tuple(str(value) for value in _tuple(response.schema_refs)),
        is_success=response.is_success,
        is_error=response.is_error,
    )


def _media_type(media_type: InferredMediaType) -> ApiMediaType:
    return ApiMediaType(
        content_type=media_type.content_type,
        schema_ref=media_type.schema_ref,
        schema_refs=tuple(str(value) for value in _tuple(media_type.schema_refs)),
    )


def _operation_target(
    target: InferredOperationTarget | None,
) -> ApiOperationTarget | None:
    if target is None:
        return None

    return ApiOperationTarget(
        ref=target.ref,
        source=target.source,
        exclude=target.exclude,
        inferred_roles=target.inferred_roles,
        locations=target.locations,
        reason=target.reason,
    )


def _dependency(dependency: InferredDependency) -> ApiDependency:
    return ApiDependency(
        source_ref=dependency.source_ref,
        target_ref=dependency.target_ref,
    )


def _query(query: QueryMetadata) -> ApiQueryOptions:
    return ApiQueryOptions(
        filterable=query.filterable,
        operators=query.operators,
        sortable=query.sortable,
        selectable=query.selectable,
        searchable=query.searchable,
        meta={RAW: query},
    )


def _tuple(value: Any) -> tuple[Any, ...]:
    """Return a tuple for optional tuple/list/set inference fields."""
    if value is None:
        return ()

    if isinstance(value, tuple):
        return value

    if isinstance(value, list | set):
        return tuple(value)

    return (value,)


def _operators(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, str):
        return (value,)

    if isinstance(value, list | tuple | set):
        return tuple(str(item) for item in value)

    return (str(value),)


def _resource_name(resource: InferredResource | None) -> str | None:
    if resource is None:
        return None

    return resource.name


def _resource_x_codegen(resource: InferredResource, x_codegen: dict[str, Any]) -> dict[str, Any]:
    resources = x_codegen.get("resources")
    if not isinstance(resources, dict):
        return {}
    value = resources.get(resource.name)
    return value if isinstance(value, dict) else {}


def _ref(value: Any) -> str | None:
    if isinstance(value, dict):
        ref = value.get("$ref")
        return str(ref) if ref else None
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _int_meta(raw: dict[str, Any], key: str, fallback: int | None) -> int | None:
    value = raw.get(key, fallback)
    return value if isinstance(value, int) and not isinstance(value, bool) else fallback


def _number_meta(
    raw: dict[str, Any],
    key: str,
    fallback: int | float | None,
) -> int | float | None:
    value = raw.get(key, fallback)
    return value if isinstance(value, int | float) and not isinstance(value, bool) else fallback


def _string_meta(raw: dict[str, Any], key: str, fallback: str | None) -> str | None:
    value = raw.get(key, fallback)
    return str(value) if value else None


def _schema_groups(schemas: tuple[ApiSchema, ...]) -> ApiSchemaGroups:
    models = _schemas_by_kind(schemas, InferredSchemaKind.MODEL)
    dtos = _schemas_by_kind(schemas, InferredSchemaKind.DTO)
    enums = _schemas_by_kind(schemas, InferredSchemaKind.ENUM)
    primitives = _schemas_by_kind(schemas, InferredSchemaKind.PRIMITIVE)
    unknown = _schemas_by_kind(schemas, InferredSchemaKind.UNKNOWN)
    aliases = tuple(schema for schema in schemas if schema.is_alias)

    return ApiSchemaGroups(
        all=schemas,
        models=models,
        dtos=dtos,
        enums=enums,
        primitives=primitives,
        aliases=aliases,
        unknown=unknown,
        emit_models=models,
        emit_dtos=dtos,
        emit_enums=enums,
    )


def _schemas_by_kind(
    schemas: tuple[ApiSchema, ...],
    kind: InferredSchemaKind,
) -> tuple[ApiSchema, ...]:
    return tuple(schema for schema in schemas if schema.kind == kind.value)
