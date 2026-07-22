"""Shared context helpers for TypeScript template contract building."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contracts.api import ApiContract
from contracts.names import NameSet
from languages.typescript.constants import DEFAULT_API_VERSION
from languages.typescript.names import safe_contract_name, safe_ts_package_name


@dataclass(frozen=True)
class TypeScriptBuildContext:
    """Prepared TypeScript package-level build facts."""

    api: ApiContract
    output_path: Path
    template_root: Path | None
    dry_run: bool
    package_name: str
    project_name: NameSet
    version: str


def build_typescript_context(
    *,
    api: ApiContract,
    output_path: Path,
    template_root: Path | None,
    dry_run: bool,
) -> TypeScriptBuildContext:
    """Build package-level TypeScript context facts."""
    title = _api_title(api)
    package_name = safe_ts_package_name(title)
    project_name = safe_contract_name(package_name)

    return TypeScriptBuildContext(
        api=api,
        output_path=output_path,
        template_root=template_root,
        dry_run=dry_run,
        package_name=package_name,
        project_name=project_name,
        version=_api_version(api),
    )


def _api_title(api: ApiContract) -> str:
    info = getattr(api, "info", None)
    title = getattr(info, "title", None)

    if isinstance(title, str) and title.strip():
        return title

    return "generated-api"


def _api_version(api: ApiContract) -> str:
    return DEFAULT_API_VERSION
