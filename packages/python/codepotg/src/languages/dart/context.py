"""Shared context helpers for Dart template contract building."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contracts.api import ApiContract
from contracts.names import NameSet
from languages.dart.constants import DEFAULT_API_VERSION
from languages.dart.names import safe_contract_name, safe_dart_package_name


@dataclass(frozen=True)
class DartBuildContext:
    """Prepared Dart package-level build facts."""

    api: ApiContract
    output_path: Path
    template_root: Path | None
    dry_run: bool
    package_name: str
    project_name: NameSet
    version: str


def build_dart_context(
    *,
    api: ApiContract,
    output_path: Path,
    template_root: Path | None,
    dry_run: bool,
) -> DartBuildContext:
    """Build package-level Dart context facts."""
    title = _api_title(api)
    package_name = safe_dart_package_name(title)
    project_name = safe_contract_name(package_name)

    return DartBuildContext(
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

    return "generated_api"


def _api_version(api: ApiContract) -> str:
    info = getattr(api, "info", None)
    version = getattr(info, "api_version", None)

    if isinstance(version, str) and version.strip():
        return version.strip().strip("/") or DEFAULT_API_VERSION

    return DEFAULT_API_VERSION
