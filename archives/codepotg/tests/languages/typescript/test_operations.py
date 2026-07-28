"""Tests for TypeScript operation template metadata."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiEntity,
    ApiEntityConstraint,
    ApiEntityField,
    ApiEntityRelation,
    ApiEnumValue,
    ApiField,
    ApiFieldKind,
    ApiFieldType,
    ApiOperation,
    ApiOperationTarget,
    ApiParameter,
    ApiRequestBody,
    ApiResource,
    ApiResponse,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
)
from archives.codepotg.src.contracts.names import make_contract_name
from archives.codepotg.src.languages.typescript.adapter import TypeScriptLanguageAdapter


def make_enum_value(value: str) -> ApiEnumValue:
    return ApiEnumValue(value=value, name=make_contract_name(value))


def test_typescript_operation_uses_parameter_target_as_query_type(tmp_path: Path) -> None:
    query_ref = "#/components/schemas/UserListQuery"

    api = ApiContract(
        info=ApiDocumentInfo(title="Query API", api_version="v1"),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="UserListQuery",
                    name=make_contract_name("UserListQuery"),
                    ref=query_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="users",
                ),
            ),
        ),
        operations=(
            ApiOperation(
                id="listUsers",
                name=make_contract_name("listUsers"),
                method="get",
                path="/users",
                resource="users",
                parameters=(
                    ApiParameter(
                        id="page",
                        name=make_contract_name("page"),
                        location="query",
                        schema_ref="#/components/schemas/SharedPage",
                    ),
                ),
                target=ApiOperationTarget(
                    ref=query_ref,
                    source="x-codegen.parameters.target",
                    inferred_roles=("query",),
                    locations=("query",),
                ),
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.query_ref == query_ref
    assert operation.meta.query_type == "UserListQuery"


def test_typescript_operation_exposes_request_content_type_flags(tmp_path: Path) -> None:
    body_ref = "#/components/schemas/UploadFileBody"

    api = ApiContract(
        info=ApiDocumentInfo(title="Upload API", api_version="v1"),
        resources=(
            ApiResource(
                id="uploads",
                name=make_contract_name("uploads"),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="UploadFileBody",
                    name=make_contract_name("UploadFileBody"),
                    ref=body_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="uploads",
                ),
            ),
        ),
        operations=(
            ApiOperation(
                id="uploadFile",
                name=make_contract_name("uploadFile"),
                method="post",
                path="/uploads",
                resource="uploads",
                request_body=ApiRequestBody(
                    required=True,
                    content_types=("multipart/form-data",),
                    schema_refs=(body_ref,),
                ),
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.request_content_types == ("multipart/form-data",)
    assert operation.meta.request_content_type == "multipart/form-data"
    assert operation.meta.is_multipart_request is True
    assert operation.meta.is_json_request is False


def test_typescript_operation_exposes_codegen_ui_metadata(tmp_path: Path) -> None:
    api = ApiContract(
        info=ApiDocumentInfo(title="UI API", api_version="v1"),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                operations_count=1,
            ),
        ),
        operations=(
            ApiOperation(
                id="listUsers",
                name=make_contract_name("listUsers"),
                method="get",
                path="/users",
                resource="users",
                meta={
                    "ui": {
                        "enabled": True,
                        "role": "list",
                        "inferred": True,
                        "inferenceSource": "compiler",
                        "inferenceReason": "GET collection route",
                    }
                },
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.ui_enabled is True
    assert operation.meta.ui_role == "list"
    assert operation.meta.ui_inferred is True
    assert operation.meta.ui_inference_source == "compiler"
    assert operation.meta.ui_inference_reason == "GET collection route"


def test_typescript_operation_keeps_codegen_ui_disabled_by_default(tmp_path: Path) -> None:
    api = ApiContract(
        info=ApiDocumentInfo(title="UI API", api_version="v1"),
        resources=(
            ApiResource(
                id="auth",
                name=make_contract_name("auth"),
                operations_count=1,
            ),
        ),
        operations=(
            ApiOperation(
                id="login",
                name=make_contract_name("login"),
                method="post",
                path="/auth/login",
                resource="auth",
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.ui_enabled is False
    assert operation.meta.ui_role is None
    assert operation.meta.ui_inferred is False


def test_typescript_operation_exposes_ui_list_response_metadata(tmp_path: Path) -> None:
    user_ref = "#/components/schemas/UserPartial"
    response_ref = "#/components/schemas/UsersListResponse"
    pagination_ref = "#/components/schemas/PaginationMeta"

    api = ApiContract(
        info=ApiDocumentInfo(title="UI API", api_version="v1"),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="UserPartial",
                    name=make_contract_name("UserPartial"),
                    ref=user_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="users",
                ),
                ApiSchema(
                    id="PaginationMeta",
                    name=make_contract_name("PaginationMeta"),
                    ref=pagination_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="shared",
                ),
                ApiSchema(
                    id="UsersListResponse",
                    name=make_contract_name("UsersListResponse"),
                    ref=response_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="users",
                    fields=(
                        ApiField(
                            id="users",
                            name=make_contract_name("users"),
                            type=ApiFieldType(
                                kind=ApiFieldKind.ARRAY,
                                item_kind=ApiFieldKind.DTO,
                            ),
                            item_ref=user_ref,
                            item_refs=(user_ref,),
                        ),
                        ApiField(
                            id="pagination",
                            name=make_contract_name("pagination"),
                            type=ApiFieldType(
                                kind=ApiFieldKind.DTO,
                                type="PaginationMeta",
                            ),
                            schema_ref=pagination_ref,
                            schema_refs=(pagination_ref,),
                        ),
                    ),
                ),
            ),
            dtos=(),
        ),
        operations=(
            ApiOperation(
                id="listUsers",
                name=make_contract_name("listUsers"),
                method="get",
                path="/users",
                resource="users",
                responses=(
                    ApiResponse(
                        status_code="200",
                        schema_refs=(response_ref,),
                        is_success=True,
                    ),
                ),
                meta={
                    "ui": {
                        "enabled": True,
                        "role": "list",
                        "inferred": True,
                    }
                },
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.ui_list_field == "users"
    assert operation.meta.ui_list_item_type == "UserPartial"
    assert operation.meta.ui_pagination_field == "pagination"


def test_typescript_operation_exposes_ui_query_field_metadata(tmp_path: Path) -> None:
    query_ref = "#/components/schemas/UserListQuery"
    filters_ref = "#/components/schemas/UserFilters"
    filterable_ref = "#/components/schemas/UserFilterable"
    sort_ref = "#/components/schemas/UserSort"
    select_ref = "#/components/schemas/UserSelect"

    api = ApiContract(
        info=ApiDocumentInfo(title="UI API", api_version="v1"),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="UserSort",
                    name=make_contract_name("UserSort"),
                    ref=sort_ref,
                    kind=ApiSchemaKind.ENUM,
                    enum_values=(
                        make_enum_value("email"),
                        make_enum_value("-createdAt"),
                        make_enum_value("+updatedAt"),
                    ),
                ),
                ApiSchema(
                    id="UserSelect",
                    name=make_contract_name("UserSelect"),
                    ref=select_ref,
                    kind=ApiSchemaKind.ENUM,
                    enum_values=(
                        make_enum_value("email"),
                        make_enum_value("status"),
                    ),
                ),
                ApiSchema(
                    id="UserFilterable",
                    name=make_contract_name("UserFilterable"),
                    ref=filterable_ref,
                    kind=ApiSchemaKind.DTO,
                    fields=(
                        ApiField(id="email", name=make_contract_name("email")),
                        ApiField(id="status", name=make_contract_name("status")),
                    ),
                ),
                ApiSchema(
                    id="UserFilters",
                    name=make_contract_name("UserFilters"),
                    ref=filters_ref,
                    kind=ApiSchemaKind.DTO,
                    inherited_refs=(filterable_ref,),
                    fields=(
                        ApiField(id="createdAt", name=make_contract_name("createdAt")),
                    ),
                ),
                ApiSchema(
                    id="UserListQuery",
                    name=make_contract_name("UserListQuery"),
                    ref=query_ref,
                    kind=ApiSchemaKind.DTO,
                    fields=(
                        ApiField(
                            id="sort",
                            name=make_contract_name("sort"),
                            type=ApiFieldType(kind=ApiFieldKind.ARRAY),
                            item_ref=sort_ref,
                            item_refs=(sort_ref,),
                        ),
                        ApiField(
                            id="fields",
                            name=make_contract_name("fields"),
                            type=ApiFieldType(kind=ApiFieldKind.ARRAY),
                            item_ref=select_ref,
                            item_refs=(select_ref,),
                        ),
                        ApiField(
                            id="filters",
                            name=make_contract_name("filters"),
                            schema_ref=filters_ref,
                            schema_refs=(filters_ref,),
                        ),
                    ),
                ),
            ),
        ),
        operations=(
            ApiOperation(
                id="listUsers",
                name=make_contract_name("listUsers"),
                method="get",
                path="/users",
                resource="users",
                target=ApiOperationTarget(
                    ref=query_ref,
                    source="x-codegen.parameters.target",
                    inferred_roles=("query",),
                    locations=("query",),
                ),
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.ui_sort_fields == ("email", "createdAt", "updatedAt")
    assert operation.meta.ui_filter_fields == ("email", "status", "createdAt")
    assert operation.meta.ui_select_fields == ("email", "status")


def test_typescript_field_exposes_referenced_enum_metadata(tmp_path: Path) -> None:
    status_ref = "#/components/schemas/UserStatus"
    body_ref = "#/components/schemas/CreateUserBody"

    api = ApiContract(
        info=ApiDocumentInfo(title="Enum API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="UserStatus",
                    name=make_contract_name("UserStatus"),
                    ref=status_ref,
                    kind=ApiSchemaKind.ENUM,
                    enum_values=(
                        make_enum_value("active"),
                        make_enum_value("emailVerified"),
                    ),
                ),
                ApiSchema(
                    id="CreateUserBody",
                    name=make_contract_name("CreateUserBody"),
                    ref=body_ref,
                    kind=ApiSchemaKind.DTO,
                    fields=(
                        ApiField(
                            id="status",
                            name=make_contract_name("status"),
                            type=ApiFieldType(kind=ApiFieldKind.ENUM),
                            schema_ref=status_ref,
                            schema_refs=(status_ref,),
                        ),
                    ),
                ),
            ),
            dtos=(
                ApiSchema(
                    id="CreateUserBody",
                    name=make_contract_name("CreateUserBody"),
                    ref=body_ref,
                    kind=ApiSchemaKind.DTO,
                    fields=(
                        ApiField(
                            id="status",
                            name=make_contract_name("status"),
                            type=ApiFieldType(kind=ApiFieldKind.ENUM),
                            schema_ref=status_ref,
                            schema_refs=(status_ref,),
                        ),
                    ),
                ),
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    field = contract.schemas.all[1].fields[0]

    assert field.meta.enum_type == "UserStatus"
    assert field.meta.enum_ref == status_ref
    assert tuple(option.wire for option in field.meta.enum_options) == (
        "active",
        "emailVerified",
    )


def test_typescript_operation_exposes_use_case_metadata_and_operation_access(
    tmp_path: Path,
) -> None:
    params_ref = "#/components/schemas/AppRouteParams"
    query_ref = "#/components/schemas/AppListQuery"
    body_ref = "#/components/schemas/CreateAppBody"
    response_ref = "#/components/schemas/AppResponse"
    context_ref = "#/components/schemas/AuthUserContext"

    api = ApiContract(
        info=ApiDocumentInfo(title="Backend API", api_version="v1"),
        resources=(
            ApiResource(
                id="apps",
                name=make_contract_name("apps"),
                path=("platform",),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                _schema("AppRouteParams", params_ref),
                _schema("AppListQuery", query_ref),
                _schema("CreateAppBody", body_ref),
                _schema("AppResponse", response_ref),
                _schema("AuthUserContext", context_ref),
            ),
        ),
        operations=(
            ApiOperation(
                id="createApp",
                name=make_contract_name("createApp"),
                method="post",
                path="/apps/{appId}",
                resource="apps",
                parameters=(
                    ApiParameter(
                        id="appId",
                        name=make_contract_name("appId"),
                        location="path",
                        required=True,
                        schema_ref=params_ref,
                    ),
                ),
                target=ApiOperationTarget(
                    ref=query_ref,
                    source="x-codegen.parameters.target",
                    inferred_roles=("query",),
                    locations=("query",),
                ),
                request_body=ApiRequestBody(required=True, schema_refs=(body_ref,)),
                responses=(
                    ApiResponse(
                        status_code="201",
                        schema_refs=(response_ref,),
                        is_success=True,
                    ),
                ),
                meta={
                    "x-codegen": {
                        "access": {"$ref": "#/x-codegen/access/user"},
                        "tags": ["apps"],
                        "cache": {"invalidate": ["apps"]},
                        "sources": {"kind": "contract"},
                    },
                },
            ),
        ),
        meta={
            "x-codegen": {
                "access": {
                    "user": {"context": {"$ref": context_ref}},
                },
            },
        },
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.resource is not None
    assert operation.resource.name.kebab.o == "apps"
    assert operation.resource.path == ("platform",)
    assert operation.meta.nest_path == "apps/:appId"
    assert operation.meta.path_params == ("appId",)
    assert operation.meta.params_type == "AppRouteParams"
    assert operation.meta.query_type == "AppListQuery"
    assert operation.meta.body_type == "CreateAppBody"
    assert operation.meta.response_type == "AppResponse"
    assert operation.meta.access_ref == "#/x-codegen/access/user"
    assert operation.meta.access_context_ref == context_ref
    assert operation.meta.access_context_type == "AuthUserContext"
    assert operation.meta.payload_type == "CreateAppPayload"
    assert operation.meta.use_case_interface == "CreateAppUseCase"
    assert operation.meta.use_case_impl_class == "CreateAppUseCaseImpl"
    assert operation.meta.use_case_file_name == "create-app.use-case"
    assert operation.meta.use_case_types_file_name == "create-app.use-case.types"
    assert operation.meta.controller_method_name == "createApp"
    assert operation.meta.service_method_name == "createApp"
    assert operation.meta.tags == ("apps",)
    assert operation.meta.cache == {"invalidate": ["apps"]}
    assert operation.meta.source == {"kind": "contract"}


def test_typescript_operation_access_context_falls_back_to_resource_access(
    tmp_path: Path,
) -> None:
    context_ref = "#/components/schemas/AuthUserContext"

    api = ApiContract(
        info=ApiDocumentInfo(title="Backend API", api_version="v1"),
        resources=(
            ApiResource(
                id="apps",
                name=make_contract_name("apps"),
                path=("platform",),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(all=(_schema("AuthUserContext", context_ref),)),
        operations=(
            ApiOperation(
                id="findApps",
                name=make_contract_name("findApps"),
                method="get",
                path="/apps",
                resource="apps",
            ),
        ),
        meta={
            "x-codegen": {
                "resources": {
                    "apps": {
                        "route": "apps",
                        "access": {"$ref": "#/x-codegen/access/user"},
                    },
                },
                "access": {
                    "user": {"context": {"$ref": context_ref}},
                },
            },
        },
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.resource is not None
    assert operation.resource.route == "apps"
    assert operation.meta.access_ref == "#/x-codegen/access/user"
    assert operation.meta.access_context_type == "AuthUserContext"


def test_typescript_entities_are_available_on_contract_and_resource(tmp_path: Path) -> None:
    app_ref = "#/components/schemas/App"
    status_ref = "#/components/schemas/AppStatus"

    api = ApiContract(
        info=ApiDocumentInfo(title="Entity API", api_version="v1"),
        resources=(
            ApiResource(
                id="apps",
                name=make_contract_name("apps"),
                path=("platform",),
                operations_count=0,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="AppStatus",
                    name=make_contract_name("AppStatus"),
                    ref=status_ref,
                    kind=ApiSchemaKind.ENUM,
                    enum_values=(make_enum_value("active"),),
                ),
                ApiSchema(
                    id="App",
                    name=make_contract_name("App"),
                    ref=app_ref,
                    kind=ApiSchemaKind.MODEL,
                    resource="apps",
                ),
            ),
        ),
        entities=(
            ApiEntity(
                id="apps.App",
                name=make_contract_name("App"),
                resource="apps",
                schema_ref=app_ref,
                store="apps",
                fields=(
                    ApiEntityField(
                        id="status",
                        name=make_contract_name("status"),
                        schema_ref=status_ref,
                        default="active",
                        type=ApiFieldType(kind=ApiFieldKind.ENUM),
                    ),
                    ApiEntityField(
                        id="type",
                        name=make_contract_name("type"),
                        max_length=300,
                        type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
                    ),
                ),
                backend_fields=(
                    ApiEntityField(
                        id="keyHash",
                        name=make_contract_name("keyHash"),
                        meta={"backend_only": True, "x-codegen": {"type": "string"}},
                    ),
                ),
                constraints=(
                    ApiEntityConstraint(
                        id="app_status_idx",
                        name=make_contract_name("app_status_idx"),
                        kind="index",
                        fields=("status",),
                    ),
                ),
                relations=(
                    ApiEntityRelation(
                        id="apiKeys",
                        name=make_contract_name("apiKeys"),
                        cardinality="hasMany",
                        target_ref="#/x-codegen/entities/apps/AppApiKey",
                    ),
                ),
            ),
            ApiEntity(
                id="apps.AppApiKey",
                name=make_contract_name("AppApiKey"),
                resource="apps",
                relations=(
                    ApiEntityRelation(
                        id="app",
                        name=make_contract_name("app"),
                        cardinality="belongsTo",
                        target_ref="#/x-codegen/entities/apps/App",
                        foreign="appId",
                    ),
                ),
            ),
        ),
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    entity = contract.entities[0]
    resource = contract.resources[0]

    assert entity.meta.class_name == "AppEntity"
    assert entity.meta.file_name == "app.entity"
    assert entity.meta.schema_type == "App"
    assert entity.meta.table_name == "apps"
    assert entity.resource is not None
    assert entity.resource.path == ("platform",)
    assert entity.fields[0].lang.type == "ApiTypes.AppStatus"
    assert entity.fields[0].meta.column_type == "simple-enum"
    assert entity.fields[0].meta.enum_type == "AppStatus"
    assert entity.fields[0].meta.column_options == (
        "type: 'simple-enum', name: 'status', enum: ApiTypes.AppStatus, "
        'nullable: false, default: "active"'
    )
    assert entity.fields[1].lang.display_name == "type"
    assert entity.fields[1].meta.column_type == "text"
    assert entity.backend_fields[0].meta.backend_only is True
    assert entity.constraints[0].kind == "index"
    assert entity.constraints[0].fields == ("status",)
    assert entity.relations[0].target_class_name == "AppApiKeyEntity"
    assert tuple(item.meta.class_name for item in resource.entities) == (
        "AppEntity",
        "AppApiKeyEntity",
    )
    assert contract.entities[1].relations[0].inverse_field_name == "apiKeys"


def _schema(name: str, ref: str) -> ApiSchema:
    return ApiSchema(
        id=name,
        name=make_contract_name(name),
        ref=ref,
        kind=ApiSchemaKind.DTO,
        resource="apps",
    )
