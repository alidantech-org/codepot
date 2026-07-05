"""TypeScript operation template builders.

This module prepares operation facts from the OpenAPI/API contract.

It must not know about NestJS decorators, Express handlers, HTTP clients,
multipart implementation details, or TypeScript import paths. Templates own
framework syntax. Import planners own generated-file import statements.
"""

from __future__ import annotations

import re

from constants.codegen import (
    ENABLED,
    INFERENCE_REASON,
    INFERENCE_SOURCE,
    INFERRED,
    ROLE,
    UI,
)
from contracts.api import (
    ApiField,
    ApiOperation,
    ApiParameter,
    ApiRequestBody,
    ApiResponse,
    ApiSchema,
)
from contracts.template import (
    TemplateDependency,
    TemplateDependencyPurpose,
    TemplateDocs,
    TemplateGroup,
    TemplateItemEmit,
    TemplateItemKey,
    TemplateOperation,
    TemplateOperationLang,
    TemplateOperationMeta,
    TemplateOperationResource,
    TemplateParameter,
    TemplateParameterLang,
    TemplateParameterMeta,
    TemplateRequestBody,
    TemplateRequestBodyLang,
    TemplateRequestBodyMeta,
    TemplateResponse,
    TemplateResponseLang,
    TemplateResponseMeta,
)
from languages.debug.context.path_values import safe_file_name
from languages.typescript.dependencies import dependency
from languages.typescript.names import name_text, safe_ts_identifier

_PATH_PARAM_PATTERN = re.compile(r"\{([^{}]+)\}")

_CONTENT_JSON = "application/json"
_CONTENT_MULTIPART = "multipart/form-data"
_CONTENT_FORM_URL_ENCODED = "application/x-www-form-urlencoded"
_CONTENT_OCTET_STREAM = "application/octet-stream"
_CONTENT_TEXT = "text/plain"


def template_operations(
    operations: tuple[ApiOperation, ...],
    *,
    resource_paths: dict[str, tuple[str, ...]],
    resources_by_id: dict[str, object] | None = None,
    schema_by_ref: dict[str, ApiSchema],
    x_codegen: dict[str, object] | None = None,
) -> tuple[TemplateOperation, ...]:
    """Build TypeScript operation template variables."""
    return tuple(
        _operation(
            operation,
            resource_paths=resource_paths,
            resources_by_id=resources_by_id or {},
            schema_by_ref=schema_by_ref,
            x_codegen=x_codegen or {},
        )
        for operation in operations
    )


def operations_for_resource(
    operations: tuple[TemplateOperation, ...],
    resource_path: tuple[str, ...],
) -> tuple[TemplateOperation, ...]:
    """Return operations belonging to a resource path."""
    return tuple(
        operation
        for operation in operations
        if operation.emit is not None and operation.emit.resource_path == resource_path
    )


def _operation(
    operation: ApiOperation,
    *,
    resource_paths: dict[str, tuple[str, ...]],
    resources_by_id: dict[str, object],
    schema_by_ref: dict[str, ApiSchema],
    x_codegen: dict[str, object],
) -> TemplateOperation:
    resource_path = _operation_resource_path(operation, resource_paths)
    method = _operation_method(operation)
    function_name = safe_ts_identifier(operation.name.camel.o, fallback="request")
    file_name = (
        f"{method}_{safe_file_name(name_text(operation.name.path.o), fallback=operation.id)}"
    )

    dependencies = _operation_dependencies(operation, schema_by_ref)
    query_ref = _query_ref(operation)
    params_ref = _params_ref(operation)
    body_ref = _body_ref(operation)
    response_ref = _success_response_ref(operation)
    list_field = _list_response_field(response_ref, schema_by_ref)
    path_params = _path_param_names(operation.path)
    request_content_types = _request_content_types(operation)
    access_ref = _access_ref(operation)
    resource_access_ref = _resource_access_ref(operation, x_codegen)
    access_context_ref = _access_context_ref(access_ref or resource_access_ref, x_codegen)
    use_case_base = operation.name.pascal.o

    return TemplateOperation(
        api=operation,
        name=operation.name,
        parameters=tuple(
            _parameter(parameter, schema_by_ref) for parameter in operation.parameters
        ),
        request_body=(
            _request_body(operation.request_body, schema_by_ref)
            if operation.request_body is not None
            else None
        ),
        responses=tuple(_response(response, schema_by_ref) for response in operation.responses),
        resource=_operation_resource(operation, resource_paths, resources_by_id, x_codegen),
        lang=TemplateOperationLang(
            kind="typescript_operation",
            function_name=function_name,
            display_name=operation.name.pascal.o,
            method=method,
        ),
        emit=TemplateItemEmit(
            group=TemplateGroup.OPERATIONS,
            item_key=TemplateItemKey.OPERATION,
            key=operation.id,
            ref=None,
            path_parts=(TemplateGroup.OPERATIONS.value, operation.name.path.o),
            resource_path=resource_path,
            folder_path=(*resource_path, "operations"),
            file_name=file_name,
            relative_doc_path=(*resource_path, "operations", f"{file_name}.ts"),
            dependency_refs=_operation_dependency_refs(operation),
            dependencies=dependencies,
            imports=tuple(item for item in dependencies if item.is_importable),
        ),
        docs=TemplateDocs(description=operation.description),
        meta=TemplateOperationMeta(
            parameter_count=len(operation.parameters),
            response_count=len(operation.responses),
            has_request_body=operation.request_body is not None,
            request_content_types=request_content_types,
            request_content_type=_first(request_content_types),
            is_json_request=_has_content_type(request_content_types, _CONTENT_JSON),
            is_multipart_request=_has_content_type(request_content_types, _CONTENT_MULTIPART),
            is_form_url_encoded_request=_has_content_type(
                request_content_types,
                _CONTENT_FORM_URL_ENCODED,
            ),
            is_octet_stream_request=_has_content_type(
                request_content_types,
                _CONTENT_OCTET_STREAM,
            ),
            is_text_request=_has_content_type(request_content_types, _CONTENT_TEXT),
            target_ref=operation.target.ref if operation.target else None,
            query_ref=query_ref,
            query_type=_schema_type(query_ref, schema_by_ref),
            params_ref=params_ref,
            params_type=_schema_type(params_ref, schema_by_ref),
            body_ref=body_ref,
            body_type=_schema_type(body_ref, schema_by_ref),
            response_ref=response_ref,
            response_type=_schema_type(response_ref, schema_by_ref),
            route_getter=function_name,
            path_params=path_params,
            has_path_params=bool(path_params),
            nest_path=_nest_path(operation.path),
            access_ref=access_ref or resource_access_ref,
            access_context_ref=access_context_ref,
            access_context_type=_schema_type(access_context_ref, schema_by_ref) or "unknown",
            tags=_operation_tags(operation),
            cache=_operation_cache(operation),
            source=_operation_sources(operation),
            info=x_codegen.get("info", {}) if isinstance(x_codegen.get("info"), dict) else {},
            payload_type=f"{use_case_base}Payload",
            use_case_interface=f"{use_case_base}UseCase",
            use_case_class=f"{use_case_base}UseCase",
            use_case_impl_class=f"{use_case_base}UseCaseImpl",
            use_case_file_name=(
                f"{safe_file_name(name_text(operation.name.kebab.o), fallback=operation.id)}"
                ".use-case"
            ),
            use_case_types_file_name=(
                f"{safe_file_name(name_text(operation.name.kebab.o), fallback=operation.id)}"
                ".use-case.types"
            ),
            controller_method_name=function_name,
            service_method_name=function_name,
            ui_enabled=_ui_enabled(operation),
            ui_role=_ui_role(operation),
            ui_inferred=_ui_inferred(operation),
            ui_inference_source=_ui_inference_source(operation),
            ui_inference_reason=_ui_inference_reason(operation),
            ui_list_field=list_field.name.camel.o if list_field else None,
            ui_list_item_type=_field_item_type(list_field, schema_by_ref),
            ui_pagination_field=_pagination_field(response_ref, schema_by_ref),
            ui_sort_fields=_query_sort_fields(query_ref, schema_by_ref),
            ui_filter_fields=_query_filter_fields(query_ref, schema_by_ref),
            ui_select_fields=_query_select_fields(query_ref, schema_by_ref),
        ),
    )


def _operation_resource(
    operation: ApiOperation,
    resource_paths: dict[str, tuple[str, ...]],
    resources_by_id: dict[str, object],
    x_codegen: dict[str, object],
) -> TemplateOperationResource | None:
    if operation.resource is None:
        return None
    resource = resources_by_id.get(operation.resource)
    name = getattr(resource, "name", None)
    if name is None:
        from contracts.names import make_contract_name

        name = make_contract_name(operation.resource)
    resource_x_codegen = _resource_x_codegen(operation.resource, x_codegen)
    return TemplateOperationResource(
        name=name,
        path=getattr(resource, "path", ()) if resource is not None else (),
        route=str(resource_x_codegen.get("route")) if resource_x_codegen.get("route") else None,
    )


def _parameter(
    parameter: ApiParameter,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateParameter:
    refs = _parameter_dependency_refs(parameter)

    return TemplateParameter(
        api=parameter,
        name=parameter.name,
        lang=TemplateParameterLang(
            kind="typescript_parameter",
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
            dependency_refs=refs,
            dependencies=tuple(
                dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_PARAMETER,
                    reason=f"Parameter {parameter.name.camel.o} uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
                for ref in refs
            ),
        ),
        meta=TemplateParameterMeta(ref=parameter.ref),
    )


def _request_body(
    request_body: ApiRequestBody,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateRequestBody:
    dependencies = tuple(
        dependency(
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
            kind=_schema_type(_first(request_body.schema_refs), schema_by_ref) or "unknown",
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
            imports=tuple(item for item in dependencies if item.is_importable),
        ),
        meta=TemplateRequestBodyMeta(
            ref=request_body.ref,
            media_type_count=len(request_body.media_types),
        ),
    )


def _response(
    response: ApiResponse,
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateResponse:
    dependencies = tuple(
        dependency(
            ref=ref,
            purpose=TemplateDependencyPurpose.OPERATION_RESPONSE,
            reason=f"Response {response.status_code} uses schema ref {ref}",
            schema_by_ref=schema_by_ref,
        )
        for ref in response.schema_refs
    )

    return TemplateResponse(
        api=response,
        lang=TemplateResponseLang(
            kind=_schema_type(_first(response.schema_refs), schema_by_ref) or "unknown",
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
            dependencies=dependencies,
            imports=tuple(item for item in dependencies if item.is_importable),
        ),
        meta=TemplateResponseMeta(
            ref=response.ref,
            media_type_count=len(response.media_types),
        ),
    )


def _operation_dependencies(
    operation: ApiOperation,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateDependency, ...]:
    deps: list[TemplateDependency] = []

    for parameter in operation.parameters:
        for ref in _parameter_dependency_refs(parameter):
            deps.append(
                dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_PARAMETER,
                    reason=f"Parameter {parameter.name.camel.o} uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    if operation.request_body is not None:
        for ref in operation.request_body.schema_refs:
            deps.append(
                dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_REQUEST_BODY,
                    reason=f"Request body uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    for response in operation.responses:
        for ref in response.schema_refs:
            deps.append(
                dependency(
                    ref=ref,
                    purpose=TemplateDependencyPurpose.OPERATION_RESPONSE,
                    reason=f"Response {response.status_code} uses schema ref {ref}",
                    schema_by_ref=schema_by_ref,
                )
            )

    if operation.target is not None:
        deps.append(
            dependency(
                ref=operation.target.ref,
                purpose=TemplateDependencyPurpose.OPERATION_TARGET,
                reason=f"Operation target uses schema ref {operation.target.ref}",
                schema_by_ref=schema_by_ref,
            )
        )

    return tuple(deps)


def _operation_dependency_refs(operation: ApiOperation) -> tuple[str, ...]:
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


def _parameter_dependency_refs(parameter: ApiParameter) -> tuple[str, ...]:
    refs: list[str] = []

    for ref in (parameter.schema_ref, *parameter.schema_refs):
        _append_ref(refs, ref)

    return tuple(refs)


def _query_ref(operation: ApiOperation) -> str | None:
    if operation.target is not None and _target_has_role(operation.target, "query"):
        return operation.target.ref

    for parameter in operation.parameters:
        if parameter.location == "query":
            return parameter.schema_ref or _first(parameter.schema_refs)

    return None


def _target_has_role(target: object, role: str) -> bool:
    roles = getattr(target, "inferred_roles", ())
    locations = getattr(target, "locations", ())

    return role in roles or role in locations


def _params_ref(operation: ApiOperation) -> str | None:
    for parameter in operation.parameters:
        if parameter.location == "path":
            return parameter.schema_ref or _first(parameter.schema_refs)

    return None


def _body_ref(operation: ApiOperation) -> str | None:
    if operation.request_body is None:
        return None

    return _first(operation.request_body.schema_refs)


def _request_content_types(operation: ApiOperation) -> tuple[str, ...]:
    if operation.request_body is None:
        return ()

    return tuple(
        _normalize_content_type(content_type)
        for content_type in operation.request_body.content_types
        if _normalize_content_type(content_type)
    )


def _has_content_type(content_types: tuple[str, ...], expected: str) -> bool:
    expected = _normalize_content_type(expected)
    return any(content_type == expected for content_type in content_types)


def _normalize_content_type(value: str) -> str:
    return value.split(";", 1)[0].strip().lower()


def _success_response_ref(operation: ApiOperation) -> str | None:
    for response in operation.responses:
        if response.is_success:
            return _first(response.schema_refs)

    return None


def _schema_type(ref: str | None, schema_by_ref: dict[str, ApiSchema]) -> str | None:
    if ref is None:
        return None

    schema = schema_by_ref.get(ref)
    if schema is None:
        return None

    return schema.name.pascal.o


def _list_response_field(
    ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> ApiField | None:
    if ref is None:
        return None

    schema = schema_by_ref.get(ref)
    if schema is None:
        return None

    for field in schema.fields:
        kind = getattr(field.type.kind, "value", field.type.kind)
        if kind == "array":
            return field

    return None


def _field_item_type(
    field: ApiField | None,
    schema_by_ref: dict[str, ApiSchema],
) -> str | None:
    if field is None:
        return None

    for ref in (field.item_ref, *field.item_refs):
        schema = schema_by_ref.get(ref)
        if schema is not None:
            return schema.name.pascal.o

    if field.type.item_type:
        return _schema_type(field.type.item_type, schema_by_ref) or field.type.item_type

    return None


def _pagination_field(ref: str | None, schema_by_ref: dict[str, ApiSchema]) -> str | None:
    if ref is None:
        return None

    schema = schema_by_ref.get(ref)
    if schema is None:
        return None

    for field in schema.fields:
        name = field.name.camel.o
        field_type = str(field.type.type or "")
        if name in {"pagination", "meta", "paginationMeta"} or field_type.endswith(
            "PaginationMeta"
        ):
            return name

    return None


def _query_sort_fields(
    query_ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[str, ...]:
    query_schema = _schema_for_ref(query_ref, schema_by_ref)
    if query_schema is None:
        return ()

    for field in query_schema.fields:
        if field.name.camel.o != "sort":
            continue

        return _enum_field_names(field, schema_by_ref)

    return ()


def _query_select_fields(
    query_ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[str, ...]:
    query_schema = _schema_for_ref(query_ref, schema_by_ref)
    if query_schema is None:
        return ()

    for field in query_schema.fields:
        if field.name.camel.o not in {"fields", "select"}:
            continue

        return _enum_field_names(field, schema_by_ref)

    return ()


def _query_filter_fields(
    query_ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[str, ...]:
    query_schema = _schema_for_ref(query_ref, schema_by_ref)
    if query_schema is None:
        return ()

    for field in query_schema.fields:
        if field.name.camel.o != "filters":
            continue

        refs = (field.schema_ref, *field.schema_refs, field.item_ref, *field.item_refs)
        for ref in refs:
            filter_schema = _schema_for_ref(ref, schema_by_ref)
            if filter_schema is not None:
                return tuple(
                    filter_field.name.camel.o
                    for filter_field in _schema_fields_with_inheritance(
                        filter_schema,
                        schema_by_ref,
                    )
                )

    return ()


def _enum_field_names(
    field: ApiField,
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[str, ...]:
    values = field.enum_values

    refs = (field.schema_ref, *field.schema_refs, field.item_ref, *field.item_refs)
    for ref in refs:
        schema = _schema_for_ref(ref, schema_by_ref)
        if schema is not None and schema.enum_values:
            values = tuple(value.value for value in schema.enum_values)
            break

    names: list[str] = []
    for value in values:
        name = str(value).strip()
        if name.startswith(("-", "+")):
            name = name[1:]
        if name and name not in names:
            names.append(name)

    return tuple(names)


def _schema_for_ref(
    ref: str | None,
    schema_by_ref: dict[str, ApiSchema],
) -> ApiSchema | None:
    if ref is None:
        return None

    return schema_by_ref.get(ref)


def _schema_fields_with_inheritance(
    schema: ApiSchema,
    schema_by_ref: dict[str, ApiSchema],
    seen_refs: tuple[str, ...] = (),
) -> tuple[ApiField, ...]:
    if schema.ref in seen_refs:
        return schema.fields

    fields: list[ApiField] = []
    next_seen_refs = (*seen_refs, schema.ref)

    for ref in (*schema.inherited_refs, schema.alias_of):
        parent = _schema_for_ref(ref, schema_by_ref)
        if parent is not None:
            fields.extend(
                _schema_fields_with_inheritance(
                    parent,
                    schema_by_ref,
                    next_seen_refs,
                )
            )

    existing = {field.name.camel.o for field in fields}
    for field in schema.fields:
        if field.name.camel.o not in existing:
            fields.append(field)

    return tuple(fields)


def _path_param_names(path: str) -> tuple[str, ...]:
    names: list[str] = []

    for match in _PATH_PARAM_PATTERN.finditer(path):
        name = safe_ts_identifier(match.group(1), fallback="param")
        if name not in names:
            names.append(name)

    return tuple(names)


def _nest_path(path: str) -> str:
    value = path.strip("/")
    for name in _path_param_names(path):
        value = value.replace(f"{{{name}}}", f":{name}")
    return value


def _operation_resource_path(
    operation: ApiOperation,
    resource_paths: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    if operation.resource and operation.resource in resource_paths:
        return resource_paths[operation.resource]

    return ("shared",)


def _operation_method(operation: ApiOperation) -> str:
    method = operation.method.value if hasattr(operation.method, "value") else str(operation.method)
    return method.lower()


def _first(values: tuple[str, ...]) -> str | None:
    return values[0] if values else None


def _ui_metadata(operation: ApiOperation) -> dict:
    ui = operation.meta.get(UI)
    return ui if isinstance(ui, dict) else {}


def _operation_x_codegen(operation: ApiOperation) -> dict[str, object]:
    value = operation.meta.get("x-codegen")
    return value if isinstance(value, dict) else {}


def _operation_tags(operation: ApiOperation) -> tuple[str, ...]:
    tags = _operation_x_codegen(operation).get("tags")
    return tuple(str(tag) for tag in tags) if isinstance(tags, list | tuple) else ()


def _operation_cache(operation: ApiOperation) -> dict[str, object]:
    value = _operation_x_codegen(operation).get("cache")
    return value if isinstance(value, dict) else {}


def _operation_sources(operation: ApiOperation) -> dict[str, object]:
    value = _operation_x_codegen(operation).get("sources")
    return value if isinstance(value, dict) else {}


def _access_ref(operation: ApiOperation) -> str | None:
    access = _operation_x_codegen(operation).get("access")
    return _ref(access)


def _resource_access_ref(operation: ApiOperation, x_codegen: dict[str, object]) -> str | None:
    if operation.resource is None:
        return None
    resource = _resource_x_codegen(operation.resource, x_codegen)
    return _ref(resource.get("access"))


def _access_context_ref(access_ref: str | None, x_codegen: dict[str, object]) -> str | None:
    if not access_ref:
        return None
    prefix = "#/x-codegen/access/"
    if not access_ref.startswith(prefix):
        return None
    parts = access_ref[len(prefix) :].split("/")
    current: object = x_codegen.get("access")
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    if not isinstance(current, dict):
        return None
    return _ref(current.get("context"))


def _resource_x_codegen(resource_id: str, x_codegen: dict[str, object]) -> dict[str, object]:
    resources = x_codegen.get("resources")
    if not isinstance(resources, dict):
        return {}
    resource = resources.get(resource_id)
    return resource if isinstance(resource, dict) else {}


def _ref(value: object) -> str | None:
    if isinstance(value, dict):
        ref = value.get("$ref")
        return str(ref) if ref else None
    return None


def _ui_enabled(operation: ApiOperation) -> bool:
    return _ui_metadata(operation).get(ENABLED) is True


def _ui_role(operation: ApiOperation) -> str | None:
    role = _ui_metadata(operation).get(ROLE)
    return role if isinstance(role, str) else None


def _ui_inferred(operation: ApiOperation) -> bool:
    return _ui_metadata(operation).get(INFERRED) is True


def _ui_inference_source(operation: ApiOperation) -> str | None:
    source = _ui_metadata(operation).get(INFERENCE_SOURCE)
    return source if isinstance(source, str) else None


def _ui_inference_reason(operation: ApiOperation) -> str | None:
    reason = _ui_metadata(operation).get(INFERENCE_REASON)
    return reason if isinstance(reason, str) else None


def _append_ref(refs: list[str], ref: str | None) -> None:
    if ref and ref not in refs:
        refs.append(ref)
