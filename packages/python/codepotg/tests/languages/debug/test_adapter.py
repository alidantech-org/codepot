"""Tests for the debug language adapter."""

from __future__ import annotations

from src.contracts.api import ApiContract, ApiDocumentInfo, ApiEnumValue, ApiResource, ApiSchema, ApiSchemaGroups
from src.contracts.names import make_contract_name
from src.languages.discovery import resolve_language_adapter
from src.languages.debug.context.path_values import safe_file_name, safe_path_parts
from tests.fixtures.contracts import make_api_contract


def test_debug_adapter_builds_template_contract(tmp_path) -> None:
    adapter = resolve_language_adapter("debug")
    api = make_api_contract()

    contract = adapter.build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    assert contract.lang.name == "debug"
    assert contract.api.info.title == "Test API"
    assert contract.emit.dry_run is True
    assert len(contract.resources) == 1
    assert len(contract.schemas.all) == 1

    resource = contract.resources[0]
    assert resource.path == ("platform", "auth")
    assert resource.path_name is not None
    assert resource.path_name.path.original == "platform_auth"
    assert resource.emit is not None
    assert resource.emit.resource_path == ("platform", "auth", "users")
    assert resource.emit.folder_path == ("platform", "auth", "users")
    assert resource.emit.file_name == "index"
    assert resource.emit.relative_doc_path == ("platform", "auth", "users", "index.md")

    model = contract.schemas.emit_models[0]
    assert model.emit is not None
    assert model.emit.resource_path == ("platform", "auth", "users")
    assert model.emit.folder_path == ("platform", "auth", "users", "schemas", "model")
    assert model.emit.file_name == "user"
    assert model.emit.relative_doc_path == (
        "platform",
        "auth",
        "users",
        "schemas",
        "model",
        "user.md",
    )
    assert model.emit.imports == tuple(dependency for dependency in model.emit.dependencies if dependency.is_importable)

    operation = contract.operations[0]
    assert operation.emit is not None
    assert operation.emit.resource_path == ("platform", "auth", "users")
    assert operation.emit.folder_path == ("platform", "auth", "users", "operations")
    assert operation.emit.file_name == "get_list_users"
    assert operation.emit.relative_doc_path == ("platform", "auth", "users", "operations", "get_list_users.md")
    assert resource.operations == (operation,)
    assert resource.models == (model,)
    assert resource.dtos == ()
    assert resource.enums == ()
    assert resource.schemas == (model,)


def test_debug_adapter_adds_resource_paths_to_dtos_and_enums(tmp_path) -> None:
    adapter = resolve_language_adapter("debug")
    dto = ApiSchema(
        id="CreateUserBody",
        name=make_contract_name("CreateUserBody"),
        kind="dto",
        ref="#/components/schemas/CreateUserBody",
        resource="users",
    )
    enum = ApiSchema(
        id="UserStatus",
        name=make_contract_name("UserStatus"),
        kind="enum",
        ref="#/components/schemas/UserStatus",
        resource="users",
        enum_values=(
            ApiEnumValue(value="active", name=make_contract_name("active")),
            ApiEnumValue(value="suspended", name=make_contract_name("suspended")),
        ),
    )
    api = ApiContract(
        info=ApiDocumentInfo(title="Test API"),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                path=("platform", "auth"),
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(dto, enum),
            dtos=(dto,),
            enums=(enum,),
            emit_dtos=(dto,),
            emit_enums=(enum,),
        ),
    )

    contract = adapter.build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    assert contract.schemas.emit_dtos[0].emit is not None
    assert contract.schemas.emit_dtos[0].emit.resource_path == ("platform", "auth", "users")
    assert contract.schemas.emit_enums[0].emit is not None
    assert contract.schemas.emit_enums[0].emit.resource_path == ("platform", "auth", "users")
    assert contract.schemas.emit_enums[0].meta.enum_values == ("active", "suspended")
    assert contract.schemas.emit_enums[0].meta.enum_count == 2

    resource = contract.resources[0]
    assert resource.dtos == (contract.schemas.emit_dtos[0],)
    assert resource.enums == (contract.schemas.emit_enums[0],)
    assert resource.schemas == (contract.schemas.emit_dtos[0], contract.schemas.emit_enums[0])


def test_debug_adapter_falls_back_to_shared_resource_path(tmp_path) -> None:
    adapter = resolve_language_adapter("debug")
    schema = ApiSchema(
        id="SharedModel",
        name=make_contract_name("SharedModel"),
        kind="model",
        ref="#/components/schemas/SharedModel",
        resource=None,
    )
    api = ApiContract(
        info=ApiDocumentInfo(title="Test API"),
        resources=(
            ApiResource(
                id="empty",
                name=make_contract_name("empty"),
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(schema,),
            models=(schema,),
            emit_models=(schema,),
        ),
    )

    contract = adapter.build_template_contract(
        api=api,
        output_path=tmp_path,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    assert contract.resources[0].emit is not None
    assert contract.resources[0].emit.resource_path == ("shared",)
    assert contract.schemas.emit_models[0].emit is not None
    assert contract.schemas.emit_models[0].emit.resource_path == ("shared",)
    assert contract.resources[0].models == (contract.schemas.emit_models[0],)
    assert contract.resources[0].schemas == (contract.schemas.emit_models[0],)


def test_debug_path_value_helpers() -> None:
    assert safe_path_parts(("platform", "auth")) == ("platform", "auth")
    assert safe_path_parts("platform/auth") == ("platform", "auth")
    assert safe_path_parts("../platform/./auth") == ("platform", "auth")
    assert safe_path_parts(None) == ("shared",)
    assert safe_file_name(("platform", "auth")) == "platform_auth"
