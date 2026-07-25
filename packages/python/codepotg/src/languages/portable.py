"""Shared foundation for portable language adapters.

The portable adapters intentionally reuse the complete typed debug contract as the
language-neutral variable baseline. They replace only project/language metadata and
post-generation guidance. This keeps every schema, operation, entity, frontend,
dependency, raw source, extension, and file-context variable available consistently
while target-specific type enrichers are added independently.
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


@dataclass(frozen=True)
class PortableLanguageProfile:
    """Metadata and safe post-generation hints for one target language."""

    name: str
    format: str
    purpose: str
    framework: str = "standard-library"
    package_suffix: str = "client"
    diagnostics: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


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
    """Build a complete typed contract without re-parsing source dictionaries."""

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
    package_name = f"{project_name.snake.o}_{profile.package_suffix}"
    server_urls = tuple(server.url for server in api.servers if server.url)
    common_meta = {
        "api_version": api.info.api_version,
        "openapi_version": api.info.openapi_version,
        "server_urls": server_urls,
        "adapter_family": "portable",
        "complete_variable_contract": True,
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
        framework=TemplateFramework(name=profile.framework),
        package=TemplatePackage(name=package_name, version="0.1.0"),
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
