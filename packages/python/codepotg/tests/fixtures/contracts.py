"""Contract fixture helpers."""

from __future__ import annotations

from pathlib import Path

from src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiOperation,
    ApiResource,
    ApiSchema,
    ApiSchemaGroups,
    ApiServer,
)
from src.contracts.names import make_contract_name
from src.contracts.template import (
    TemplateContract,
    TemplateEmit,
    TemplateLanguage,
    TemplateProject,
    TemplateResource,
    TemplateSchema,
    TemplateSchemaGroups,
)


def make_api_contract() -> ApiContract:
    """Create a small API contract for tests."""
    user_schema = ApiSchema(
        id="User",
        name=make_contract_name("User"),
        kind="model",
        ref="#/components/schemas/User",
        resource="users",
    )

    return ApiContract(
        info=ApiDocumentInfo(
            title="Test API",
            openapi_version="3.1.0",
            api_version="v1",
        ),
        resources=(
            ApiResource(
                id="users",
                name=make_contract_name("users"),
                path=("platform", "auth"),
                path_name=make_contract_name("platform_auth"),
                operations_count=1,
            ),
        ),
        servers=(
            ApiServer(
                url="https://api.example.test",
                description="Test API",
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(user_schema,),
            models=(user_schema,),
            emit_models=(user_schema,),
        ),
        operations=(
            ApiOperation(
                id="listUsers",
                name=make_contract_name("listUsers"),
                method="get",
                path="/users",
                resource="users",
            ),
        ),
    )


def make_template_contract(output_path: Path, template_root: Path | None = None) -> TemplateContract:
    """Create a small template contract for emission tests."""
    api = make_api_contract()

    template_schema = TemplateSchema(api=api.schemas.all[0], name=api.schemas.all[0].name)

    return TemplateContract(
        project=TemplateProject(name=make_contract_name("test_package")),
        api=api,
        lang=TemplateLanguage(name="debug"),
        emit=TemplateEmit(output_path=output_path, template_root=template_root, dry_run=False),
        resources=(
            TemplateResource(
                api=api.resources[0],
                name=api.resources[0].name,
                path=api.resources[0].path,
                path_name=api.resources[0].path_name,
            ),
        ),
        schemas=TemplateSchemaGroups(
            all=(template_schema,),
            models=(template_schema,),
            emit_models=(template_schema,),
        ),
    )
