"""Base template render context contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from archives.codepot.src.contracts.language.exports import LanguageExport
from archives.codepot.src.contracts.language.imports import LanguageImport
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.context import SpecCounts, SpecMetadata
from archives.codepot.src.contracts.templates.config.selection import TemplateSelect
from archives.codepot.src.contracts.templates.shared.dependencies import TemplateDependencies
from archives.codepot.src.contracts.templates.shared.paths import TemplatePathContext


@dataclass(frozen=True)
class TemplateProjectContext:
    """Project metadata exposed to every template."""

    key: str
    title: str
    version: str
    spec_version: int
    codepot_version: str
    summary: str | None = None


@dataclass(frozen=True)
class TemplateSpecContext:
    """Small spec summary exposed to every template."""

    metadata: SpecMetadata
    counts: SpecCounts


@dataclass(frozen=True)
class TemplateConfigContext:
    """Current template entry metadata exposed to every template."""

    id: str
    kind: str
    select: TemplateSelect
    source: str
    is_template: bool
    is_copy: bool
    has_barrel: bool = False


@dataclass(frozen=True)
class TemplateGlobalContext:
    """Global template settings exposed to every template."""

    alias: str
    package_path: Path
    output_root: Path
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class TemplateBaseContext:
    """Base context included in every Jinja render context.

    Selection-specific contexts should compose this instead of redefining
    project/spec/language/template/path/import/dependency fields.
    """

    global_context: TemplateGlobalContext
    project: TemplateProjectContext
    spec: TemplateSpecContext
    language: LanguageRuntime
    template: TemplateConfigContext
    path: TemplatePathContext

    imports: tuple[LanguageImport, ...] = ()
    exports: tuple[LanguageExport, ...] = ()
    dependencies: TemplateDependencies | None = None
