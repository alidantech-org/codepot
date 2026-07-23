"""TypeScript language adapter."""

from __future__ import annotations

from pathlib import Path

from contracts.api import ApiContract
from contracts.emission import EmissionResult
from contracts.events import ProgressSink, RuntimeEvent
from contracts.language import LanguagePostResult
from contracts.template import (
    TemplateContract,
    TemplateContractMeta,
    TemplateDocs,
    TemplateEmit,
    TemplateFeatures,
    TemplateFramework,
    TemplateLanguage,
    TemplatePackage,
    TemplateProject,
    TemplateProjectEmit,
    TemplateProjectLang,
)
from inference.frontends import all_template_frontends, template_frontends
from languages.decorators import language_adapter
from languages.typescript.constants import (
    NODE_FRAMEWORK_NAME,
    TYPESCRIPT_LANGUAGE_ALIAS_TS,
    TYPESCRIPT_LANGUAGE_NAME,
    TYPESCRIPT_TEMPLATE_NAME,
)
from languages.typescript.context import build_typescript_context
from languages.typescript.entities import template_entities
from languages.typescript.operations import template_operations
from languages.typescript.resources import resource_paths, template_resources
from languages.typescript.schemas import template_schema_groups
from languages.typescript.urls import default_base_url


@language_adapter(
    name=TYPESCRIPT_LANGUAGE_NAME,
    aliases=(TYPESCRIPT_LANGUAGE_ALIAS_TS,),
    template_name=TYPESCRIPT_TEMPLATE_NAME,
)
class TypeScriptLanguageAdapter:
    """Build TypeScript template contracts from the API contract."""

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
        """Build deterministic TypeScript template variables."""
        _notify(progress, "building_typescript_contract", "Building TypeScript template contract")

        context = build_typescript_context(
            api=api,
            output_path=output_path,
            template_root=template_root,
            dry_run=dry_run,
        )

        resource_path_map = resource_paths(api.resources)
        schemas = template_schema_groups(api, resource_paths=resource_path_map)
        schema_by_ref = {schema.ref: schema for schema in api.schemas.all}
        resources_by_id = {resource.id: resource for resource in api.resources}
        entities = template_entities(
            api.entities,
            resource_paths=resource_path_map,
            resources_by_id=resources_by_id,
            schema_by_ref=schema_by_ref,
        )
        operations = template_operations(
            api.operations,
            resource_paths=resource_path_map,
            resources_by_id=resources_by_id,
            schema_by_ref=schema_by_ref,
            x_codegen=api.meta.get("x-codegen", {}),
        )
        resources = template_resources(
            api.resources,
            schemas=schemas,
            operations=operations,
            entities=entities,
        )
        server_urls = tuple(server.url for server in api.servers if server.url)
        servers = tuple(
            {
                "url": server.url,
                "description": server.description,
                "variables": server.variables,
            }
            for server in api.servers
        )
        all_frontends = all_template_frontends(api.meta.get("x-codegen", {}))
        selected_frontends = template_frontends(api.meta.get("x-codegen", {}), selected=frontend)
        selected_frontend = selected_frontends[0] if frontend and frontend != "*" and selected_frontends else None

        return TemplateContract(
            project=TemplateProject(
                name=context.project_name,
                version="0.1.0",
                description=_project_description(api),
                lang=TemplateProjectLang(
                    name=TYPESCRIPT_LANGUAGE_NAME,
                    purpose="TypeScript API SDK",
                ),
                emit=TemplateProjectEmit(
                    format="typescript",
                    root_path=output_path,
                ),
                docs=TemplateDocs(
                    summary="Generated TypeScript API SDK",
                    description=_project_description(api),
                ),
                meta={
                    "default_base_url": default_base_url(api),
                    "server_urls": server_urls,
                    "servers": servers,
                    "api_version": context.version,
                },
            ),
            api=api,
            resources=resources,
            schemas=schemas,
            operations=operations,
            entities=entities,
            frontends=all_frontends,
            selected_frontend=selected_frontend,
            selected_frontends=selected_frontends,
            frontend_count=len(all_frontends),
            lang=TemplateLanguage(
                name=self.name,
                framework=TemplateFramework(name=NODE_FRAMEWORK_NAME),
                package=TemplatePackage(
                    name=context.package_name,
                    version="0.1.0",
                ),
                features=TemplateFeatures(),
                meta={
                    "api_version": context.version,
                    "default_base_url": default_base_url(api),
                    "server_urls": server_urls,
                    "servers": servers,
                },
            ),
            emit=TemplateEmit(
                output_path=output_path,
                template_root=template_root,
                dry_run=dry_run,
                contract_version="1.0",
            ),
            meta=TemplateContractMeta(
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
        """Return TypeScript post-action hints without running tools yet."""
        _notify(
            progress,
            "typescript_post_actions",
            "TypeScript post-actions are informational for now",
        )
        return LanguagePostResult(
            diagnostics=(
                "Run `npm install` in the generated package if package files are emitted.",
                "Run `npx prettier --write .` after generation.",
            )
        )


def _project_description(api: ApiContract) -> str:
    description = api.info.description.strip()

    if description and description != "-":
        return description

    return ""


def _notify(progress: ProgressSink | None, stage: str, message: str) -> None:
    """Emit a progress event."""
    if progress is None:
        return

    progress(RuntimeEvent(stage=stage, message=message))
