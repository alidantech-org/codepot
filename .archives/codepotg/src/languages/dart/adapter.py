"""Dart language adapter."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.contracts.api import ApiContract
from archives.codepotg.src.contracts.emission import EmissionResult
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.language import LanguagePostResult
from archives.codepotg.src.contracts.names import make_contract_name
from archives.codepotg.src.contracts.template import (
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
from archives.codepotg.src.inference.frontends import all_template_frontends, template_frontends
from archives.codepotg.src.languages.dart.constants import (
    DART_LANGUAGE_ALIAS_FLUTTER,
    DART_LANGUAGE_NAME,
    DART_TEMPLATE_NAME,
    FLUTTER_FRAMEWORK_NAME,
)
from archives.codepotg.src.languages.dart.context import build_dart_context
from archives.codepotg.src.languages.dart.operations import template_operations
from archives.codepotg.src.languages.dart.resources import feature_resources, resource_paths, template_resources
from archives.codepotg.src.languages.dart.schemas import template_schema_groups
from archives.codepotg.src.languages.dart.urls import default_base_url
from archives.codepotg.src.languages.decorators import language_adapter


@language_adapter(
    name=DART_LANGUAGE_NAME,
    aliases=(DART_LANGUAGE_ALIAS_FLUTTER,),
    template_name=DART_TEMPLATE_NAME,
)
class DartLanguageAdapter:
    """Build Dart template contracts from the API contract."""

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
        """Build deterministic Dart template variables."""
        _notify(progress, "building_dart_contract", "Building Dart template contract")

        context = build_dart_context(
            api=api,
            output_path=output_path,
            template_root=template_root,
            dry_run=dry_run,
        )

        resource_path_map = resource_paths(api.resources)
        schemas = template_schema_groups(api, resource_paths=resource_path_map)
        schema_by_ref = {schema.ref: schema for schema in api.schemas.all}
        operations = template_operations(
            api.operations,
            version=context.version,
            resource_paths=resource_path_map,
            schema_by_ref=schema_by_ref,
        )
        resources = template_resources(api.resources, schemas=schemas, operations=operations)
        features = feature_resources(resources)
        api_version_name = make_contract_name(context.version)
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
                    name=DART_LANGUAGE_NAME,
                    purpose="Flutter API SDK",
                ),
                emit=TemplateProjectEmit(
                    format="dart",
                    root_path=output_path,
                ),
                docs=TemplateDocs(
                    summary="Generated Flutter API SDK",
                    description=_project_description(api),
                ),
                meta={
                    "default_base_url": default_base_url(api),
                    "server_urls": server_urls,
                    "servers": servers,
                    "api_version": context.version,
                    "api_version_name": api_version_name,
                },
            ),
            api=api,
            resources=resources,
            features=features,
            schemas=schemas,
            operations=operations,
            frontends=all_frontends,
            selected_frontend=selected_frontend,
            selected_frontends=selected_frontends,
            frontend_count=len(all_frontends),
            lang=TemplateLanguage(
                name=self.name,
                framework=TemplateFramework(name=FLUTTER_FRAMEWORK_NAME),
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
                    "api_version_name": api_version_name,
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
        """Return Dart post-action hints without running tools yet."""
        _notify(progress, "dart_post_actions", "Dart post-actions are informational for now")
        return LanguagePostResult(
            diagnostics=(
                "Run `flutter pub get` in the generated package.",
                "Run `dart format lib` after generation.",
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
