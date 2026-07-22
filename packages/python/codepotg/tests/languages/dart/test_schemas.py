"""Tests for Dart schema template preparation."""

from __future__ import annotations

from pathlib import Path

from languages.dart.adapter import DartLanguageAdapter
from src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiField,
    ApiFieldKind,
    ApiFieldType,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
)
from src.contracts.names import make_contract_name


def _field(name: str, *, required: bool = True) -> ApiField:
    return ApiField(
        id=name,
        name=make_contract_name(name),
        required=required,
        type=ApiFieldType(type="string"),
    )


def _schema_field(name: str, ref: str, *, required: bool = True, array: bool = False) -> ApiField:
    return ApiField(
        id=name,
        name=make_contract_name(name),
        required=required,
        schema_ref=None if array else ref,
        schema_refs=() if array else (ref,),
        item_ref=ref if array else None,
        item_refs=(ref,) if array else (),
        type=ApiFieldType(kind=ApiFieldKind.ARRAY if array else ApiFieldKind.MODEL),
    )


def test_dart_schema_super_fields_include_full_inheritance_chain(tmp_path: Path) -> None:
    api_message = ApiSchema(
        id="ApiMessage",
        name=make_contract_name("ApiMessage"),
        ref="#/components/schemas/ApiMessage",
        kind=ApiSchemaKind.MODEL,
        fields=(
            _field("success"),
            _field("message"),
        ),
    )
    base_query = ApiSchema(
        id="BaseQuery",
        name=make_contract_name("BaseQuery"),
        ref="#/components/schemas/BaseQuery",
        kind=ApiSchemaKind.MODEL,
        fields=(
            _field("page", required=False),
            _field("limit", required=False),
            _field("search", required=False),
        ),
        inherited_refs=(api_message.ref,),
    )
    user_list_query = ApiSchema(
        id="UserListQuery",
        name=make_contract_name("UserListQuery"),
        ref="#/components/schemas/UserListQuery",
        kind=ApiSchemaKind.MODEL,
        fields=(
            _field("filters", required=False),
            _field("fields", required=False),
            _field("sort", required=False),
        ),
        inherited_refs=(base_query.ref,),
    )

    api = ApiContract(
        info=ApiDocumentInfo(title="Dart Schema API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(api_message, base_query, user_list_query),
            models=(api_message, base_query, user_list_query),
            emit_models=(api_message, base_query, user_list_query),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    schemas_by_name = {schema.name.pascal.o: schema for schema in contract.schemas.emit_models}
    base_query_template = schemas_by_name["BaseQuery"]
    user_list_query_template = schemas_by_name["UserListQuery"]

    assert [field.lang.display_name for field in base_query_template.meta.super_fields] == [
        "success",
        "message",
    ]
    assert [field.lang.display_name for field in user_list_query_template.meta.super_fields] == [
        "success",
        "message",
        "page",
        "limit",
        "search",
    ]
    assert [field.lang.display_name for field in user_list_query_template.fields] == [
        "filters",
        "fields",
        "sort",
    ]


def test_dart_schema_imports_inherited_constructor_field_dependencies(tmp_path: Path) -> None:
    api_message = ApiSchema(
        id="ApiMessage",
        name=make_contract_name("ApiMessage"),
        ref="#/components/schemas/ApiMessage",
        kind=ApiSchemaKind.MODEL,
        fields=(
            _field("success"),
            _field("message"),
        ),
    )
    pagination_meta = ApiSchema(
        id="PaginationMeta",
        name=make_contract_name("PaginationMeta"),
        ref="#/components/schemas/PaginationMeta",
        kind=ApiSchemaKind.MODEL,
        fields=(_field("page"),),
    )
    user_partial = ApiSchema(
        id="UserPartial",
        name=make_contract_name("UserPartial"),
        ref="#/components/schemas/UserPartial",
        kind=ApiSchemaKind.MODEL,
        fields=(_field("id"),),
    )
    paginated_response = ApiSchema(
        id="PaginatedResponse",
        name=make_contract_name("PaginatedResponse"),
        ref="#/components/schemas/PaginatedResponse",
        kind=ApiSchemaKind.MODEL,
        fields=(_schema_field("pagination", pagination_meta.ref),),
        inherited_refs=(api_message.ref,),
        dependencies=(pagination_meta.ref,),
    )
    users_list_response = ApiSchema(
        id="UsersListResponse",
        name=make_contract_name("UsersListResponse"),
        ref="#/components/schemas/UsersListResponse",
        kind=ApiSchemaKind.MODEL,
        fields=(_schema_field("users", user_partial.ref, array=True),),
        inherited_refs=(paginated_response.ref,),
        dependencies=(user_partial.ref,),
    )

    api = ApiContract(
        info=ApiDocumentInfo(title="Dart Schema API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(
                api_message,
                pagination_meta,
                user_partial,
                paginated_response,
                users_list_response,
            ),
            models=(
                api_message,
                pagination_meta,
                user_partial,
                paginated_response,
                users_list_response,
            ),
            emit_models=(
                api_message,
                pagination_meta,
                user_partial,
                paginated_response,
                users_list_response,
            ),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    schemas_by_name = {schema.name.pascal.o: schema for schema in contract.schemas.emit_models}
    users_list_response_template = schemas_by_name["UsersListResponse"]

    super_field_names = [
        field.lang.display_name for field in users_list_response_template.meta.super_fields
    ]
    assert super_field_names == [
        "success",
        "message",
        "pagination",
    ]
    assert [field.lang.display_name for field in users_list_response_template.fields] == ["users"]
    assert {dependency.ref for dependency in users_list_response_template.emit.imports} == {
        paginated_response.ref,
        pagination_meta.ref,
        user_partial.ref,
    }


def test_dart_type_field_keeps_type_name_without_json_key(tmp_path: Path) -> None:
    schema = ApiSchema(
        id="CompanyPublic",
        name=make_contract_name("CompanyPublic"),
        ref="#/components/schemas/CompanyPublic",
        kind=ApiSchemaKind.MODEL,
        fields=(
            ApiField(
                id="type",
                name=make_contract_name("type"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
            ),
            ApiField(
                id="name",
                name=make_contract_name("name"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
            ),
        ),
    )

    api = ApiContract(
        info=ApiDocumentInfo(title="Dart Reserved API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(schema,),
            models=(schema,),
            emit_models=(schema,),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    fields = contract.schemas.emit_models[0].fields

    assert fields[0].lang.display_name == "type"
    assert fields[0].lang.json_key is None
    assert fields[1].lang.display_name == "name"
    assert fields[1].lang.json_key is None


def test_dart_actual_reserved_field_names_keep_wire_json_key(tmp_path: Path) -> None:
    schema = ApiSchema(
        id="ReservedPayload",
        name=make_contract_name("ReservedPayload"),
        ref="#/components/schemas/ReservedPayload",
        kind=ApiSchemaKind.MODEL,
        fields=(
            ApiField(
                id="default",
                name=make_contract_name("default"),
                type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="boolean"),
            ),
        ),
    )

    api = ApiContract(
        info=ApiDocumentInfo(title="Dart Reserved API", api_version="v1"),
        schemas=ApiSchemaGroups(
            all=(schema,),
            models=(schema,),
            emit_models=(schema,),
        ),
    )

    contract = DartLanguageAdapter().build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    field = contract.schemas.emit_models[0].fields[0]

    assert field.lang.display_name == "defaultValue"
    assert field.lang.json_key == "default"
