"""Debug language adapter."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.contracts.api import (
    ApiContract,
    ApiField,
    ApiOperation,
    ApiParameter,
    ApiResource,
    ApiResponse,
    ApiSchema,
)
from archives.codepotg.src.contracts.emission import EmissionResult
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.language import LanguagePostResult
from archives.codepotg.src.contracts.names import make_contract_name
from archives.codepotg.src.contracts.template import (
    TemplateContract,
    TemplateContractMeta,
    TemplateDependency,
    TemplateDependencyPurpose,
    TemplateDependencyTarget,
    TemplateDependencyTargetKind,
    TemplateDocs,
    TemplateEmit,
    TemplateFeatures,
    TemplateField,
    TemplateFieldLang,
    TemplateFieldMeta,
    TemplateFramework,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
    TemplateLanguage,
    TemplateOperation,
    TemplateOperationLang,
    TemplateOperationMeta,
    TemplatePackage,
    TemplateParameter,
    TemplateParameterLang,
    TemplateParameterMeta,
    TemplateProject,
    TemplateProjectEmit,
    TemplateProjectLang,
    TemplateRequestBody,
    TemplateRequestBodyLang,
    TemplateRequestBodyMeta,
    TemplateResource,
    TemplateResourceLang,
    TemplateResourceMeta,
    TemplateResponse,
    TemplateResponseLang,
    TemplateResponseMeta,
    TemplateSchema,
    TemplateSchemaGroups,
    TemplateSchemaLang,
    TemplateSchemaMeta,
)
from archives.codepotg.src.inference.frontends import all_template_frontends, template_frontends
from archives.codepotg.src.languages.debug.context.path_values import safe_file_name, safe_path_parts
from archives.codepotg.src.languages.decorators import language_adapter


@language_adapter(name="debug", aliases=("txt", "md"), template_name="debug")
class DebugLanguageAdapter:
    """Build debug template contracts from the API contract."""

    name: str
    aliases: tuple[str, ...]
    template_name: str

    def build_template_contract(
        self,
        *,
        api: ApiContract,
        output_path: Path,
        template_root: Path | None = None,
        dry_run: bool = False,
        frontend: str | None = None,
        progress: ProgressSink | None = None,
    ) -> TemplateContract:
        """Build deterministic debug template variables."""
        _notify(progress, "building_debug_contract", "Building debug template contract")

        schema_by_ref = {schema.ref: schema for schema in api.schemas.all}
        resource_paths = _resource_paths(api.resources)
        schema_resource_paths = _schema_resource_paths(api.schemas.all, resource_paths)
        operations = tuple(_operation(operation, schema_by_ref, resource_paths) for operation in api.operations)
        schemas = _schema_groups(api, schema_by_ref, schema_resource_paths)
        all_frontends = all_template_frontends(api.meta.get("x-codegen", {}))
        selected_frontends = template_frontends(api.meta.get("x-codegen", {}), selected=frontend)
        selected_frontend = selected_frontends[0] if frontend and frontend != "*" and selected_frontends else None

        return TemplateContract(
            project=TemplateProject(
                name=make_contract_name("debug"),
                version="debug",
                description="Debug text emission",
                lang=TemplateProjectLang(
                    name="debug",
                    purpose="contract inspection",
                ),
                emit=TemplateProjectEmit(
                    format="text",
                    root_path=output_path,
                ),
                docs=TemplateDocs(
                    summary="Debug contract output",
                    description="Text output used to inspect template variables.",
                ),
            ),
            api=api,
            lang=TemplateLanguage(
                name=self.name,
                framework=TemplateFramework(name="none"),
                package=TemplatePackage(name="debug"),
                features=TemplateFeatures(
                    text_reports=True,
                    schema_groups=True,
                    field_reports=True,
                    dependency_reports=True,
                    file_context_reports=True,
                ),
            ),
            emit=TemplateEmit(
                output_path=output_path,
                template_root=template_root,
                dry_run=dry_run,
                contract_version="1.0",
            ),
            resources=tuple(_resource(resource, schemas=schemas, operations=operations) for resource in api.resources),
            schemas=schemas,
            operations=operations,
            frontends=all_frontends,
            selected_frontend=selected_frontend,
            selected_frontends=selected_frontends,
            frontend_count=len(all_frontends),
            meta=TemplateContractMeta(
                debug=True,
                schema_count=len(api.schemas.all),
                model_count=len(api.schemas.emit_models),
                dto_count=len(api.schemas.emit_dtos),
                enum_count=len(api.schemas.emit_enums),
                primitive_count=len(api.schemas.primitives),
                operation_count=len(api.operations),
                resource_count=len(api.resources),
            ),
        )

    def after_emit(
        self,
        *,
        result: EmissionResult,
        progress: ProgressSink | None = None,
    ) -> LanguagePostResult:
        """Debug language has no post-actions."""
        _notify(progress, "debug_post_actions", "No debug post-actions required")
        return LanguagePostResult()


def _schema_groups(
    api: ApiContract,
    schema_by_ref: dict[str, ApiSchema],
    schema_resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchemaGroups:
    """Build typed schema groups for debug templates."""
    return TemplateSchemaGroups(
        all=tuple(
            _schema(schema, group=TemplateGroup.SCHEMAS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.all
        ),
        models=tuple(
            _schema(schema, group=TemplateGroup.MODELS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.models
        ),
        dtos=tuple(
            _schema(schema, group=TemplateGroup.DTOS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.dtos
        ),
        enums=tuple(
            _schema(schema, group=TemplateGroup.ENUMS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.enums
        ),
        primitives=tuple(
            _schema(schema, group=TemplateGroup.PRIMITIVES, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.primitives
        ),
        aliases=tuple(
            _schema(schema, group=TemplateGroup.ALIASES, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.aliases
        ),
        unknown=tuple(
            _schema(schema, group=TemplateGroup.UNKNOWN, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.unknown
        ),
        queries=tuple(
            _schema(schema, group=TemplateGroup.QUERIES, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.queries
        ),
        params=tuple(
            _schema(schema, group=TemplateGroup.PARAMS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.params
        ),
        bodies=tuple(
            _schema(schema, group=TemplateGroup.BODIES, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.bodies
        ),
        responses=tuple(
            _schema(schema, group=TemplateGroup.RESPONSES, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.responses
        ),
        emit_models=tuple(
            _schema(schema, group=TemplateGroup.MODELS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.emit_models
        ),
        emit_dtos=tuple(
            _schema(schema, group=TemplateGroup.DTOS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.emit_dtos
        ),
        emit_enums=tuple(
            _schema(schema, group=TemplateGroup.ENUMS, schema_by_ref=schema_by_ref, schema_resource_paths=schema_resource_paths)
            for schema in api.schemas.emit_enums
        ),
    )


def _resource(
    resource: ApiResource,
    *,
    schemas: TemplateSchemaGroups,
    operations: tuple[TemplateOperation, ...],
) -> TemplateResource:
    """Build typed resource template variables."""
    resource_path = _resource_path(resource)
    relative_doc_path = (*resource_path, "index.md")
    resource_operations = _items_for_resource(operations, resource_path)
    resource_models = _items_for_resource(schemas.emit_models, resource_path)
    resource_dtos = _items_for_resource(schemas.emit_dtos, resource_path)
    resource_enums = _items_for_resource(schemas.emit_enums, resource_path)
    resource_schemas = (*resource_models, *resource_dtos, *resource_enums)

    return TemplateResource(
        api=resource,
        name=resource.name,
        path=resource.path,
        path_name=resource.path_name,
        operations=resource_operations,
        models=resource_models,
        dtos=resource_dtos,
        enums=resource_enums,
        schemas=resource_schemas,
        lang=TemplateResourceLang(
            kind="debug_resource",
            display_name=resource.name.pascal.o,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.RESOURCES,
            item_key=TemplateItemKey.RESOURCE,
            key=resource.id,
            ref=None,
            path_parts=(TemplateGroup.RESOURCES.value, resource.name.path.o),
            path=relative_doc_path,
            resource_path=resource_path,
            folder_path=resource_path,
            file_name="index",
            relative_doc_path=relative_doc_path,
            dependency_refs=(),
        ),
        docs=TemplateDocs(),
        meta=TemplateResourceMeta(
            operations_count=resource.operations_count,
        ),
    )


def _schema(
    schema: ApiSchema,
    *,
    group: TemplateGroup,
    schema_by_ref: dict[str, ApiSchema],
    schema_resource_paths: dict[str, tuple[str, ...]],
) -> TemplateSchema:
    """Build typed schema template variables."""
    fields = tuple(_field(field, schema_by_ref) for field in schema.fields)
    dependencies = _schema_dependencies(schema, schema_by_ref)
    resource_path = schema_resource_paths.get(schema.ref, safe_path_parts(schema.resource))
    kind = _schema_kind_value(schema)
    file_name = safe_file_name(schema.name.path.o, fallback=schema.id)
    folder_path = (*resource_path, "schemas", kind)
    relative_doc_path = (*folder_path, f"{file_name}.md")

    return TemplateSchema(
        api=schema,
        name=schema.name,
        fields=fields,
        lang=TemplateSchemaLang(
            kind=f"debug_{schema.kind.value if hasattr(schema.kind, 'value') else schema.kind}",
            type=_schema_debug_type(schema),
            display_name=schema.name.pascal.o,
            symbol_name=schema.name.pascal.o,
            field_count=len(fields),
            dependency_count=len(schema.dependencies),
            query_enabled=schema.query.enabled,
        ),
        emit=TemplateItemEmit(
            group=group,
            item_key=_item_key_for_schema_group(group),
            key=schema.ref,
            ref=schema.ref,
            path_parts=(group.value, schema.name.path.o),
            path=relative_doc_path,
            resource_path=resource_path,
            folder_path=folder_path,
            file_name=file_name,
            relative_doc_path=relative_doc_path,
            dependency_refs=schema.dependencies,
            dependencies=dependencies,
            imports=_imports(dependencies),
        ),
        docs=TemplateDocs(
            description=schema.description,
        ),
        meta=TemplateSchemaMeta(
            is_alias=schema.is_alias,
            alias_of=schema.alias_of,
            primitive_type=schema.primitive_type,
            primitive_format=schema.primitive_format,
            enum_type=schema.enum_type,
            enum_values=tuple(value.value for value in schema.enum_values),
            enum_count=len(schema.enum_values),
            composition_refs=schema.composition_refs,
            inherited_refs=schema.inherited_refs,
            query_enabled=schema.query.enabled,
        ),
    )


def _field(field: ApiField, schema_by_ref: dict[str, ApiSchema]) -> TemplateField:
    """Build typed field template variables."""
    dependencies = _field_dependencies(field, schema_by_ref)
    return TemplateField(
        api=field,
        name=field.name,
        lang=TemplateFieldLang(
            kind="debug_field",
            type=_field_debug_type(field),
            display_name=field.name.camel.o,
            required=field.required,
            nullable=field.nullable,
            query_enabled=field.query.enabled,
            sortable=field.query.sortable,
            selectable=field.query.selectable,
            filterable=field.query.filterable,
            searchable=field.query.searchable,
            operators=field.query.operators,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.FIELDS,
            item_key=TemplateItemKey.FIELD,
            key=field.id,
            ref=field.schema_ref,
            path_parts=(TemplateGroup.FIELDS.value, field.name.path.o),
            dependency_refs=_field_dependency_refs(field),
            dependencies=dependencies,
        ),
        docs=TemplateDocs(
            description=field.description,
        ),
        meta=TemplateFieldMeta(
            default=field.default,
            enum_values=field.enum_values,
            raw_type=field.type.raw_type,
        ),
    )


def _operation(
    operation: ApiOperation,
    schema_by_ref: dict[str, ApiSchema],
    resource_paths: dict[str, tuple[str, ...]],
) -> TemplateOperation:
    """Build typed operation template variables."""
    resource_path = _operation_resource_path(operation, resource_paths)
    method = _operation_method(operation)
    file_name = f"{method}_{safe_file_name(operation.name.path.o, fallback=operation.id)}"
    folder_path = (*resource_path, "operations")
    relative_doc_path = (*folder_path, f"{file_name}.md")
    dependencies = _operation_dependencies(operation, schema_by_ref)

    return TemplateOperation(
        api=operation,
        name=operation.name,
        parameters=tuple(_parameter(parameter, schema_by_ref) for parameter in operation.parameters),
        request_body=(_request_body(operation.request_body, schema_by_ref) if operation.request_body is not None else None),
        responses=tuple(_response(response, schema_by_ref) for response in operation.responses),
        lang=TemplateOperationLang(
            kind="debug_operation",
            function_name=operation.name.snake.o,
            display_name=operation.name.pascal.o,
            method=operation.method.upper(),
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.OPERATIONS,
            item_key=TemplateItemKey.OPERATION,
            key=operation.id,
            ref=None,
            path_parts=(TemplateGroup.OPERATIONS.value, operation.name.path.o),
            path=relative_doc_path,
            resource_path=resource_path,
            folder_path=folder_path,
            file_name=file_name,
            relative_doc_path=relative_doc_path,
            dependency_refs=_operation_dependency_refs(operation),
            dependencies=dependencies,
            imports=_imports(dependencies),
        ),
        docs=TemplateDocs(
            description=operation.description,
        ),
        meta=TemplateOperationMeta(
            parameter_count=len(operation.parameters),
            response_count=len(operation.responses),
            has_request_body=operation.request_body is not None,
            target_ref=operation.target.ref if operation.target else None,
        ),
    )


def _parameter(parameter: ApiParameter, schema_by_ref: dict[str, ApiSchema]) -> TemplateParameter:
    """Build typed parameter template variables."""
    return TemplateParameter(
        api=parameter,
        name=parameter.name,
        lang=TemplateParameterLang(
            kind="debug_parameter",
            display_name=parameter.name.camel.o,
            location=parameter.location,
            required=parameter.required,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.PARAMS,
            item_key=TemplateItemKey.PARAMETER,
            key=parameter.id,
            ref=parameter.schema_ref,
            path_parts=(TemplateGroup.PARAMS.value, parameter.name.path.o),
            dependency_refs=_parameter_dependency_refs(parameter),
        ),
        docs=TemplateDocs(),
        meta=TemplateParameterMeta(
            ref=parameter.ref,
        ),
    )


def _request_body(request_body, schema_by_ref: dict[str, ApiSchema]) -> TemplateRequestBody:
    """Build typed request body template variables."""
    dependencies = tuple(
        _dependency(
            ref=ref,
            purpose=TemplateDependencyPurpose.OPERATION_REQUEST_BODY,
            reason=f"Request body uses schema ref {ref}",
            schema_by_ref=schema_by_ref,
        )
        for ref in request_body.schema_refs
    )

    return TemplateRequestBody(
        api=request_body,
        lang=TemplateRequestBodyLang(
            kind="debug_request_body",
            required=request_body.required,
            content_types=request_body.content_types,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.BODIES,
            item_key=TemplateItemKey.REQUEST,
            key=request_body.ref or "request_body",
            ref=request_body.ref,
            path_parts=(TemplateGroup.BODIES.value, "request_body"),
            dependency_refs=request_body.schema_refs,
            dependencies=dependencies,
        ),
        docs=TemplateDocs(),
        meta=TemplateRequestBodyMeta(
            ref=request_body.ref,
            media_type_count=len(request_body.media_types),
        ),
    )


def _response(response: ApiResponse, schema_by_ref: dict[str, ApiSchema]) -> TemplateResponse:
    """Build typed response template variables."""
    return TemplateResponse(
        api=response,
        lang=TemplateResponseLang(
            kind="debug_response",
            status_code=response.status_code,
            is_success=response.is_success,
            is_error=response.is_error,
            content_types=response.content_types,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.RESPONSES,
            item_key=TemplateItemKey.RESPONSE,
            key=response.ref or response.status_code,
            ref=response.ref,
            path_parts=(TemplateGroup.RESPONSES.value, response.status_code),
            dependency_refs=response.schema_refs,
        ),
        docs=TemplateDocs(
            description=response.description,
        ),
        meta=TemplateResponseMeta(
            ref=response.ref,
            media_type_count=len(response.media_types),
        ),
    )


def _schema_debug_type(schema: ApiSchema) -> str:
    """Return debug display type for a schema."""
    kind = schema.kind.value if hasattr(schema.kind, "value") else str(schema.kind)

    if kind == "primitive":
        return schema.primitive_type or "primitive"

    if kind == "enum":
        return schema.enum_type or "enum"

    return kind


def _field_debug_type(field: ApiField) -> str:
    """Return debug display type for a field."""
    if field.type.type:
        return field.type.type

    if field.type.raw_type:
        return field.type.raw_type

    if field.schema_ref:
        return field.schema_ref

    return "unknown"


def _resource_paths(resources: tuple[ApiResource, ...]) -> dict[str, tuple[str, ...]]:
    return {resource.id: _resource_path(resource) for resource in resources}


def _items_for_resource(items: tuple, resource_path: tuple[str, ...]) -> tuple:
    return tuple(item for item in items if item.emit is not None and item.emit.resource_path == resource_path)


def _schema_resource_paths(
    schemas: tuple[ApiSchema, ...],
    resource_paths: dict[str, tuple[str, ...]],
) -> dict[str, tuple[str, ...]]:
    explicit = {schema.ref: resource_paths[schema.resource] for schema in schemas if schema.resource and schema.resource in resource_paths}
    resolved = dict(explicit)

    for schema in schemas:
        if schema.ref in resolved:
            continue

        owner_path = _dependent_resource_path(
            schema.ref,
            schemas=schemas,
            explicit=explicit,
        )
        if owner_path is not None:
            resolved[schema.ref] = owner_path
            continue

        resolved[schema.ref] = safe_path_parts(schema.resource)

    return resolved


def _dependent_resource_path(
    ref: str,
    *,
    schemas: tuple[ApiSchema, ...],
    explicit: dict[str, tuple[str, ...]],
) -> tuple[str, ...] | None:
    for owner in schemas:
        if ref not in owner.dependencies:
            continue

        owner_path = explicit.get(owner.ref)
        if owner_path is not None:
            return owner_path

    return None


def _resource_path(resource: ApiResource) -> tuple[str, ...]:
    base_path = safe_path_parts(resource.path, fallback="")
    name_path = safe_path_parts(resource.name.path.o, fallback=resource.id)

    if base_path == ("",):
        return safe_path_parts(None)

    if base_path[-len(name_path) :] == name_path:
        return base_path

    return (*base_path, *name_path)


def _operation_resource_path(
    operation: ApiOperation,
    resource_paths: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    if operation.resource and operation.resource in resource_paths:
        return resource_paths[operation.resource]

    return safe_path_parts(operation.resource)


def _schema_kind_value(schema: ApiSchema) -> str:
    kind = schema.kind.value if hasattr(schema.kind, "value") else str(schema.kind)
    return kind or "schema"


def _operation_method(operation: ApiOperation) -> str:
    method = operation.method.value if hasattr(operation.method, "value") else str(operation.method)
    return method.lower()


def _schema_dependencies(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Build typed dependencies for a schema."""
    deps: list[TemplateDependency] = []

    for ref in schema.inherited_refs:
        deps.append(
            _dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.INHERITANCE,
                reason=f"{schema.name.pascal.o} inherits from {ref}",
                schema_by_ref=schema_by_ref,
                is_inheritance=True,
                owner_ref=schema.ref,
            )
        )

    for ref in schema.dependencies:
        if ref in schema.inherited_refs:
            continue

        deps.append(
            _dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=f"{schema.name.pascal.o} references {ref}",
                schema_by_ref=schema_by_ref,
                owner_ref=schema.ref,
            )
        )

    return tuple(deps)


def _field_dependencies(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    """Build typed dependencies for a field."""
    deps: list[TemplateDependency] = []

    for ref in field.schema_refs:
        deps.append(
            _dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.FIELD_TYPE,
                reason=f"Field {field.name.camel.o} uses schema ref {ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    for ref in field.item_refs:
        deps.append(
            _dependency(
                ref=ref,
                purpose=TemplateDependencyPurpose.ARRAY_ITEM,
                reason=f"Field {field.name.camel.o} uses array item ref {ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    return tuple(deps)


def _operation_dependencies(
    operation: ApiOperation,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    deps: list[TemplateDependency] = []

    for parameter in operation.parameters:
        for ref in _parameter_dependency_refs(parameter):
            deps.append(
                _dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_PARAMETER,
                    reason=f"Parameter {parameter.name.camel.o} uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    if operation.request_body is not None:
        for ref in operation.request_body.schema_refs:
            deps.append(
                _dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_REQUEST_BODY,
                    reason=f"Request body uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    for response in operation.responses:
        for ref in response.schema_refs:
            deps.append(
                _dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_RESPONSE,
                    reason=f"Response {response.status_code} uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    if operation.target is not None:
        deps.append(
            _dependency(
                ref=operation.target.ref,
                purpose=TemplateDependencyPurpose.OPERATION_TARGET,
                reason=f"Operation target uses schema ref {operation.target.ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    return tuple(deps)


def _dependency(
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
    target = _dependency_target(ref, target_schema)
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


def _imports(dependencies: tuple[TemplateDependency, ...]) -> tuple[TemplateDependency, ...]:
    return tuple(dependency for dependency in dependencies if dependency.is_importable)


def _dependency_target(
    ref: str,
    schema: ApiSchema | None,
) -> TemplateDependencyTarget:
    """Build dependency target info."""
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
    """Map schema kind to dependency target kind."""
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
    target: TemplateDependencyTarget | None,
    *,
    is_self: bool,
) -> bool:
    """Determine if dependency is importable."""
    if is_self or target is None:
        return False

    return not target.is_primitive and target.kind != TemplateDependencyTargetKind.UNKNOWN


def _field_dependency_refs(field: ApiField) -> tuple[str, ...]:
    """Return dependency refs from a field."""
    refs: list[str] = []

    for ref in (
        field.schema_ref,
        *field.schema_refs,
        field.item_ref,
        *field.item_refs,
    ):
        _append_ref(refs, ref)

    return tuple(refs)


def _parameter_dependency_refs(parameter: ApiParameter) -> tuple[str, ...]:
    """Return dependency refs from a parameter."""
    refs: list[str] = []

    for ref in (parameter.schema_ref, *parameter.schema_refs):
        _append_ref(refs, ref)

    return tuple(refs)


def _operation_dependency_refs(operation: ApiOperation) -> tuple[str, ...]:
    """Return dependency refs from an operation."""
    refs: list[str] = []

    for parameter in operation.parameters:
        for ref in _parameter_dependency_refs(parameter):
            _append_ref(refs, ref)

    if operation.request_body is not None:
        for ref in operation.request_body.schema_refs:
            _append_ref(refs, ref)

    for response in operation.responses:
        for ref in response.schema_refs:
            _append_ref(refs, ref)

    if operation.target is not None:
        _append_ref(refs, operation.target.ref)

    return tuple(refs)


def _item_key_for_schema_group(group: TemplateGroup) -> TemplateItemKey:
    """Return template item key for a schema group."""
    if group == TemplateGroup.MODELS:
        return TemplateItemKey.MODEL

    if group == TemplateGroup.DTOS:
        return TemplateItemKey.DTO

    if group == TemplateGroup.ENUMS:
        return TemplateItemKey.ENUM

    if group == TemplateGroup.PRIMITIVES:
        return TemplateItemKey.PRIMITIVE

    return TemplateItemKey.SCHEMA


def _append_ref(refs: list[str], ref: str | None) -> None:
    """Append a non-empty ref once."""
    if ref and ref not in refs:
        refs.append(ref)


def _notify(progress: ProgressSink | None, stage: str, message: str) -> None:
    """Emit a progress event."""
    if progress is None:
        return

    progress(RuntimeEvent(stage=stage, message=message))
