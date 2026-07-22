"""Tests for Dart route endpoint preparation."""

from __future__ import annotations

from pathlib import Path

from languages.dart.adapter import DartLanguageAdapter
from src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiOperation,
    ApiOperationTarget,
    ApiParameter,
    ApiRequestBody,
    ApiResource,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
)
from src.contracts.names import make_contract_name
from src.languages.dart.urls import build_endpoint_path


def test_build_endpoint_path_keeps_routes_versionless() -> None:
    assert build_endpoint_path("/auth/login") == "/auth/login"
    assert build_endpoint_path("auth/login") == "/auth/login"


def test_dart_operation_endpoint_paths_and_request_version(tmp_path: Path) -> None:
    api = ApiContract(
        info=ApiDocumentInfo(title="Route API", api_version="v1"),
        resources=(
            ApiResource(
                id="auth",
                name=make_contract_name("auth"),
                operations_count=2,
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
            ApiOperation(
                id="userById",
                name=make_contract_name("userById"),
                method="get",
                path="/users/{userId}",
                resource="auth",
            ),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    login, user_by_id = contract.operations

    assert login.lang.endpoint_path == "/auth/login"
    assert login.lang.dart_interpolated_endpoint_path == "/auth/login"
    assert login.lang.version == "v1"
    assert user_by_id.lang.endpoint_path == "/users/{userId}"
    assert user_by_id.lang.dart_interpolated_endpoint_path == "/users/$userId"
    assert user_by_id.lang.version == "v1"


def test_dart_contract_features_include_only_resources_with_operations(tmp_path: Path) -> None:
    api = ApiContract(
        info=ApiDocumentInfo(title="Feature API", api_version="v1"),
        resources=(
            ApiResource(
                id="auth",
                name=make_contract_name("auth"),
                operations_count=1,
            ),
            ApiResource(
                id="shared",
                name=make_contract_name("shared"),
                operations_count=0,
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

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    assert tuple(resource.api.id for resource in contract.resources) == ("auth", "shared")
    assert tuple(resource.api.id for resource in contract.features) == ("auth",)


def test_dart_operation_uses_parameter_target_as_query_type(tmp_path: Path) -> None:
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
            dtos=(
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

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.query_ref == query_ref
    assert operation.meta.query_type == "UserListQuery"


def test_dart_operation_keeps_path_params_separate_from_query_target(
    tmp_path: Path,
) -> None:
    query_ref = "#/components/schemas/CompanyMemberListQuery"
    mongo_id_ref = "#/components/schemas/SharedMongoId"

    api = ApiContract(
        info=ApiDocumentInfo(title="Company API", api_version="v1"),
        resources=(
            ApiResource(
                id="company-members",
                name=make_contract_name("company-members"),
                operations_count=1,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="CompanyMemberListQuery",
                    name=make_contract_name("CompanyMemberListQuery"),
                    ref=query_ref,
                    kind=ApiSchemaKind.DTO,
                    resource="company-members",
                ),
                ApiSchema(
                    id="SharedMongoId",
                    name=make_contract_name("SharedMongoId"),
                    ref=mongo_id_ref,
                    kind=ApiSchemaKind.PRIMITIVE,
                    primitive_type="string",
                ),
            ),
        ),
        operations=(
            ApiOperation(
                id="listCompanyMembers",
                name=make_contract_name("listCompanyMembers"),
                method="get",
                path="/companies/{companyId}/members",
                resource="company-members",
                parameters=(
                    ApiParameter(
                        id="companyId",
                        name=make_contract_name("companyId"),
                        location="path",
                        required=True,
                        schema_ref=mongo_id_ref,
                    ),
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
                    inferred_roles=("params", "query"),
                    locations=("path", "query"),
                ),
            ),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.query_ref == query_ref
    assert operation.meta.query_type == "CompanyMemberListQuery"
    assert operation.meta.params_ref == mongo_id_ref
    assert operation.meta.params_type is None
    assert operation.meta.path_params == ("companyId",)


def test_dart_operation_does_not_use_primitive_path_ref_as_params_type(
    tmp_path: Path,
) -> None:
    mongo_id_ref = "#/components/schemas/SharedMongoId"

    api = ApiContract(
        info=ApiDocumentInfo(title="Params API", api_version="v1"),
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
                    id="SharedMongoId",
                    name=make_contract_name("SharedMongoId"),
                    ref=mongo_id_ref,
                    kind=ApiSchemaKind.PRIMITIVE,
                    primitive_type="string",
                ),
            ),
            primitives=(
                ApiSchema(
                    id="SharedMongoId",
                    name=make_contract_name("SharedMongoId"),
                    ref=mongo_id_ref,
                    kind=ApiSchemaKind.PRIMITIVE,
                    primitive_type="string",
                ),
            ),
        ),
        operations=(
            ApiOperation(
                id="getUserById",
                name=make_contract_name("getUserById"),
                method="get",
                path="/users/{userId}",
                resource="users",
                parameters=(
                    ApiParameter(
                        id="userId",
                        name=make_contract_name("userId"),
                        location="path",
                        schema_ref=mongo_id_ref,
                    ),
                ),
            ),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    operation = contract.operations[0]

    assert operation.meta.params_ref == mongo_id_ref
    assert operation.meta.params_type is None
    assert operation.meta.path_params == ("userId",)
    assert operation.meta.has_path_params is True


def test_dart_operation_exposes_request_content_type_flags(tmp_path: Path) -> None:
    body_ref = "#/components/schemas/UploadFileBody"

    api = ApiContract(
        info=ApiDocumentInfo(title="Upload API", api_version="v1"),
        resources=(
            ApiResource(
                id="uploads",
                name=make_contract_name("uploads"),
                operations_count=2,
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
            ApiOperation(
                id="claimUpload",
                name=make_contract_name("claimUpload"),
                method="post",
                path="/uploads/claim",
                resource="uploads",
                request_body=ApiRequestBody(
                    required=True,
                    content_types=("application/json; charset=utf-8",),
                    schema_refs=(body_ref,),
                ),
            ),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    upload_file, claim_upload = contract.operations

    assert upload_file.meta.request_content_types == ("multipart/form-data",)
    assert upload_file.meta.request_content_type == "multipart/form-data"
    assert upload_file.meta.is_multipart_request is True
    assert upload_file.meta.is_json_request is False
    assert claim_upload.meta.request_content_types == ("application/json",)
    assert claim_upload.meta.is_json_request is True
    assert claim_upload.meta.is_multipart_request is False
