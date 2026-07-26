"""Shared foundation for production language adapters.

Inference remains language-neutral. Adapters reuse the complete typed contract and
attach deterministic target-language type, package, and source-layout conventions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from contracts.api import ApiContract
from contracts.emission import EmissionResult
from contracts.events import ProgressSink, RuntimeEvent
from contracts.language import LanguagePostResult
from contracts.names import make_contract_name
from contracts.template import (
    TemplateContract,
    TemplateDocs,
    TemplateFeatures,
    TemplateFramework,
    TemplateLanguage,
    TemplatePackage,
    TemplateProjectEmit,
    TemplateProjectLang,
)
from languages.debug.adapter import DebugLanguageAdapter
from languages.portable_types import PortableTypeSystem, type_system_for


@dataclass(frozen=True)
class PortableLanguageProfile:
    """Complete target metadata for one production language adapter."""

    name: str
    format: str
    purpose: str
    framework: str = "standard-library"
    package_suffix: str = "client"
    diagnostics: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    package_dependencies: tuple[str, ...] = ()
    package_dev_dependencies: tuple[str, ...] = ()
    type_system: PortableTypeSystem | None = None

    @property
    def resolved_type_system(self) -> PortableTypeSystem:
        """Return the explicit or registered type system for this target."""

        return self.type_system or type_system_for(self.name)


def build_portable_template_contract(
    profile: PortableLanguageProfile,
    *,
    api: ApiContract,
    output_path: Path,
    template_root: Path | None = None,
    dry_run: bool = False,
    frontend: str | None = None,
    progress: ProgressSink | None = None,
) -> TemplateContract:
    """Build a complete typed target contract without re-parsing source dictionaries."""

    _notify(
        progress,
        f"building_{profile.name.replace('-', '_')}_contract",
        f"Building {profile.name} template contract",
    )
    base = DebugLanguageAdapter().build_template_contract(
        api=api,
        output_path=output_path,
        template_root=template_root,
        dry_run=dry_run,
        frontend=frontend,
        progress=None,
    )
    title = api.info.title.strip() if api.info.title else ""
    project_name = make_contract_name(title or f"{profile.name} API")
    description = api.info.description.strip()
    if description == "-":
        description = ""

    type_system = profile.resolved_type_system
    package_name = f"{project_name.snake.o}_{profile.package_suffix}"
    server_urls = tuple(server.url for server in api.servers if server.url)
    common_meta = {
        "api_version": api.info.api_version,
        "openapi_version": api.info.openapi_version,
        "server_urls": server_urls,
        "adapter_family": "production-portable",
        "complete_variable_contract": True,
        "type_system": type_system,
        "scalar_types": type_system.scalar_types,
        "format_types": type_system.format_types,
        "file_extension": type_system.file_extension,
        "package_file": type_system.package_file,
        "source_root": type_system.source_root,
    }

    project = replace(
        base.project,
        name=project_name,
        description=description,
        lang=TemplateProjectLang(name=profile.name, purpose=profile.purpose),
        emit=TemplateProjectEmit(format=profile.format, root_path=output_path),
        docs=TemplateDocs(
            summary=f"Generated {profile.name} API package",
            description=description,
        ),
        meta=common_meta,
    )
    language = TemplateLanguage(
        name=profile.name,
        framework=TemplateFramework(
            name=profile.framework,
            meta={
                "source_root": type_system.source_root,
                "file_extension": type_system.file_extension,
            },
        ),
        package=TemplatePackage(
            name=package_name,
            version="0.1.0",
            dependencies=profile.package_dependencies,
            dev_dependencies=profile.package_dev_dependencies,
            meta={"manifest": type_system.package_file},
        ),
        features=TemplateFeatures(
            text_reports=True,
            schema_groups=True,
            field_reports=True,
            dependency_reports=True,
            file_context_reports=True,
        ),
        meta=common_meta,
    )
    return replace(
        base,
        project=project,
        lang=language,
        emit=replace(
            base.emit,
            output_path=output_path,
            template_root=template_root,
            dry_run=dry_run,
        ),
        meta=replace(base.meta, debug=False),
    )


def portable_after_emit(
    profile: PortableLanguageProfile,
    *,
    result: EmissionResult,
    progress: ProgressSink | None = None,
) -> LanguagePostResult:
    """Return target-specific hints without executing external tools."""

    _notify(
        progress,
        f"{profile.name.replace('-', '_')}_post_actions",
        f"{profile.name} post-actions are informational",
    )
    return LanguagePostResult(diagnostics=profile.diagnostics)


def _notify(progress: ProgressSink | None, stage: str, message: str) -> None:
    if progress is not None:
        progress(RuntimeEvent(stage=stage, message=message))
