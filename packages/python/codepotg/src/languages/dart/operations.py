"""Dart operation template builders.

This module prepares operation facts from the OpenAPI/API contract.

It must not know about Flutter API Bridge request classes, options classes,
multipart implementation details, or Dart import paths. Templates own framework
syntax. Import planners own generated-file import statements.
"""

from __future__ import annotations

import re

from contracts.api import (
    ApiOperation,
    ApiParameter,
    ApiRequestBody,
    ApiResponse,
    ApiSchema,
    ApiSchemaKind,
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
from languages.dart.dependencies import dependency
from languages.dart.names import name_text, safe_dart_identifier
from languages.dart.urls import build_endpoint_path
from languages.debug.context.path_values import safe_file_name

_PATH_PARAM_PATTERN = re.compile(r"\{([^{}]+)\}")

_CONTENT_JSON = "application/json"
_CONTENT_MULTIPART = "multipart/form-data"
_CONTENT_FORM_URL_ENCODED = "application/x-www-form-urlencoded"
_CONTENT_OCTET_STREAM = "application/octet-stream"
_CONTENT_TEXT = "text/plain"


def template_operations(
    operations: tuple[ApiOperation, ...],
    *,
    version: str,
    resource_paths: dict[str, tuple[str, ...]],
    schema_by_ref: dict[str, ApiSchema],
) -> tuple[TemplateOperation, ...]:
    """Build Dart operation template variables."""
    return tuple(
        _operation(
            operation,
            version=version,
            resource_paths=resource_paths,
            schema_by_ref=schema_by_ref,
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
    version: str,
    resource_paths: dict[str, tuple[str, ...]],
    schema_by_ref: dict[str, ApiSchema],
) -> TemplateOperation:
    resource_path = _operation_resource_path(operation, resource_paths)
    method = _operation_method(operation)
    function_name = safe_dart_identifier(operation.name.camel.o, fallback="request")
    file_name = (
        f"{method}_{safe_file_name(name_text(operation.name.path.o), fallback=operation.id)}"
    )

    dependencies = _operation_dependencies(operation, schema_by_ref)
    query_ref = _query_ref(operation)
    params_ref = _params_ref(operation)
    body_ref = _body_ref(operation)
    response_ref = _success_response_ref(operation)
    path_params = _path_param_names(operation.path)
    endpoint_path = build_endpoint_path(operation.path)
    request_content_types = _request_content_types(operation)

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
        lang=TemplateOperationLang(
            kind="dart_operation",
            function_name=function_name,
            display_name=operation.name.pascal.o,
            method=method,
            endpoint_path=endpoint_path,
            dart_interpolated_endpoint_path=_dart_interpolated_endpoint_path(endpoint_path),
            version=version,
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
            relative_doc_path=(*resource_path, "operations", f"{file_name}.dart"),
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
            params_type=_params_type(params_ref, schema_by_ref),
            body_ref=body_ref,
            body_type=_schema_type(body_ref, schema_by_ref),
            response_ref=response_ref,
            response_type=_schema_type(response_ref, schema_by_ref),
            route_getter=function_name,
            path_params=path_params,
            has_path_params=bool(path_params),
        ),
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
            kind="dart_parameter",
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
            kind=_schema_type(_first(request_body.schema_refs), schema_by_ref) or "dynamic",
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
            kind=_schema_type(_first(response.schema_refs), schema_by_ref) or "dynamic",
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


def _params_ref(operation: ApiOperation) -> str | None:
    for parameter in operation.parameters:
        if parameter.location == "path":
            return parameter.schema_ref or _first(parameter.schema_refs)

    return None


def _target_has_role(target: object, role: str) -> bool:
    roles = getattr(target, "inferred_roles", ())
    locations = getattr(target, "locations", ())

    return role in roles or role in locations


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


def _params_type(ref: str | None, schema_by_ref: dict[str, ApiSchema]) -> str | None:
    if ref is None:
        return None

    schema = schema_by_ref.get(ref)
    if schema is None:
        return None

    if schema.kind not in {ApiSchemaKind.DTO, ApiSchemaKind.MODEL}:
        return None

    return schema.name.pascal.o


def _path_param_names(path: str) -> tuple[str, ...]:
    names: list[str] = []

    for match in _PATH_PARAM_PATTERN.finditer(path):
        name = safe_dart_identifier(match.group(1), fallback="param")
        if name not in names:
            names.append(name)

    return tuple(names)


def _dart_interpolated_endpoint_path(path: str) -> str:
    return _PATH_PARAM_PATTERN.sub(
        lambda match: f"${safe_dart_identifier(match.group(1), fallback='param')}",
        path,
    )


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


def _append_ref(refs: list[str], ref: str | None) -> None:
    if ref and ref not in refs:
        refs.append(ref)
