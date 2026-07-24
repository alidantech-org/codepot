from __future__ import annotations

from dataclasses import replace
from typing import Any

from contracts.api import (
    ApiContract,
    ApiDependency,
    ApiDependencyGraph,
    ApiInfo,
    ApiOperation,
    ApiProject,
    ApiResource,
    ApiSchema,
    ApiSchemaGroups,
    ApiServer,
)
from contracts.names import build_name_set
from contracts.normalized_api import build_normalized_api_view
from contracts.source import extract_extensions, freeze_source_map
from inference.models import InferenceGraph


_SCHEMA_GROUPS = (
    "all",
    "models",
    "dtos",
    "enums",
    "primitives",
    "aliases",
    "unknown",
    "queries",
    "params",
    "bodies",
    "requests",
    "responses",
    "shared",
    "projected",
    "composed",
    "emit_models",
    "emit_dtos",
    "emit_enums",
)


def build_api_contract(graph: InferenceGraph) -> ApiContract:
    """Build the stable language-neutral API contract from inference output."""

    raw = graph.raw or {}
    raw_info = _mapping(raw.get("info"))
    schema_lookup = {schema.id: schema for schema in graph.schemas}
    schema_ref_lookup = {schema.ref: schema for schema in graph.schemas}
    operation_lookup = {operation.id: operation for operation in graph.operations}
    operation_ref_lookup = {operation.ref: operation for operation in graph.operations}
    resource_lookup = {resource.id: resource for resource in graph.resources}

    schemas = tuple(
        ApiSchema(
            id=schema.id,
            name=build_name_set(schema.name),
            ref=schema.ref,
            kind=schema.kind,
            resource=schema.resource,
            role=schema.role,
            fields=schema.fields,
            is_alias=schema.is_alias,
            alias_of=schema.alias_of,
            primitive_type=schema.primitive_type,
            primitive_format=schema.primitive_format,
            enum_type=schema.enum_type,
            enum_values=schema.enum_values,
            composition_refs=schema.composition_refs,
            inherited_refs=schema.inherited_refs,
            dependencies=schema.dependencies,
            query=schema.query,
            meta={
                **dict(schema.meta),
                "shared": schema.shared,
                "projection_source": schema.projection_source,
                "projection_include": schema.projection_include,
                "projection_exclude": schema.projection_exclude,
                "projection_rename": dict(schema.projection_rename),
                "projection_partial": schema.projection_partial,
            },
        )
        for schema in graph.schemas
    )
    api_schemas_by_id = {schema.id: schema for schema in schemas}

    operations = tuple(
        ApiOperation(
            id=operation.id,
            name=build_name_set(operation.name),
            ref=operation.ref,
            method=operation.method,
            path=operation.path,
            kind=operation.kind,
            resource=operation.resource,
            parameters=operation.parameters,
            request_body=operation.request_body,
            responses=operation.responses,
            query_schema_ref=operation.query_schema_ref,
            params_schema_ref=operation.params_schema_ref,
            body_schema_ref=operation.body_schema_ref,
            response_schema_ref=operation.response_schema_ref,
            target_schema_ref=operation.target_schema_ref,
            cache=operation.cache,
            access=operation.access,
            runtime=operation.runtime,
            hooks=operation.hooks,
            sources=operation.sources,
            ui=operation.ui,
            meta=dict(operation.meta),
        )
        for operation in graph.operations
    )
    api_operations_by_id = {operation.id: operation for operation in operations}

    resources = tuple(
        ApiResource(
            id=resource.id,
            name=build_name_set(resource.name),
            path=resource.path,
            path_name=build_name_set(resource.path_name),
            operations=tuple(
                api_operations_by_id[operation.id]
                for operation in resource.operations
                if operation.id in api_operations_by_id
            ),
            schemas=tuple(
                api_schemas_by_id[schema.id]
                for schema in resource.schemas
                if schema.id in api_schemas_by_id
            ),
            meta=dict(resource.meta),
        )
        for resource in graph.resources
    )

    dependencies = tuple(
        ApiDependency(
            source_ref=dependency.source_ref,
            target_ref=dependency.target_ref,
            kind=dependency.kind,
            reason=dependency.reason,
        )
        for dependency in graph.dependencies
    )

    grouped = {
        group: tuple(
            api_schemas_by_id[schema.id]
            for schema in graph.schema_groups.get(group, ())
            if schema.id in api_schemas_by_id
        )
        for group in _SCHEMA_GROUPS
    }

    root_meta = {
        **dict(graph.meta),
        "servers": tuple(raw.get("servers", ()) or ()),
        "security": tuple(raw.get("security", ()) or ()),
        "tags": tuple(raw.get("tags", ()) or ()),
        "external_docs": raw.get("externalDocs"),
        "webhooks": raw.get("webhooks"),
        "components": raw.get("components"),
        "json_schema_dialect": raw.get("jsonSchemaDialect"),
    }
    contract = ApiContract(
        project=ApiProject(
            id=graph.title,
            name=build_name_set(graph.title),
            version=graph.version,
            description=graph.description,
            meta={"openapi_version": graph.openapi_version},
        ),
        info=ApiInfo(
            title=graph.title,
            openapi_version=graph.openapi_version,
            api_version=graph.version,
            description=graph.description,
            extensions=extract_extensions(raw_info),
            raw=freeze_source_map(raw_info),
            meta={
                "terms_of_service": raw_info.get("termsOfService"),
                "contact": raw_info.get("contact"),
                "license": raw_info.get("license"),
            },
        ),
        servers=tuple(
            ApiServer(
                url=str(server.get("url", "-")),
                description=str(server.get("description", "-")),
                extensions=extract_extensions(server),
                raw=freeze_source_map(server),
                meta={"variables": server.get("variables", {})},
            )
            for value in tuple(raw.get("servers", ()) or ())
            if isinstance(value, dict)
            for server in (value,)
        ),
        resources=resources,
        schemas=ApiSchemaGroups(**grouped),
        operations=operations,
        dependencies=ApiDependencyGraph(all=dependencies),
        raw=freeze_source_map(raw),
        extensions=extract_extensions(raw),
        meta=root_meta,
    )
    normalized = build_normalized_api_view(contract, graph.raw)
    return replace(
        contract,
        meta={
            **contract.meta,
            "normalized": normalized,
            "loss_count": normalized.loss_count,
            "unresolved_count": normalized.unresolved_count,
            "raw_only_count": normalized.raw_only_count,
        },
    )


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}
