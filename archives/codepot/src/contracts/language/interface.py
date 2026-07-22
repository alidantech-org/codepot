"""Language adapter interface contract.

This module defines the exact methods every Codepotx language adapter must
implement. The pipeline calls adapters through this interface only.

Language adapters should:
- create global language runtime context
- enrich selected spec/template items with `.lang`
- create type annotations
- create file-level imports
- create file-level exports

Language adapters should not:
- load specs
- select records
- plan files
- render templates
- write files
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from archives.codepot.src.contracts.language.context import (
    LanguageField,
    LanguageItem,
    LanguageOperation,
    LanguageRoute,
)
from archives.codepot.src.contracts.language.exports import LanguageExport, LanguageExportStrategy
from archives.codepot.src.contracts.language.imports import LanguageImport
from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.language.types import LanguageType
from archives.codepot.src.contracts.spec.names import SpecName
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.config.language import (
    TemplateLanguageImportConfig,
    TemplateLanguageNamingConfig,
)
from archives.codepot.src.contracts.templates.shared.flags import TemplateFieldFlags


@dataclass(frozen=True)
class LanguageRuntimeRequest:
    """Request used to create global language runtime context."""

    language: str
    extensions: tuple[str, ...]
    package_name: str | None
    package_manager: str | None
    source_root: Path
    naming: TemplateLanguageNamingConfig
    imports: TemplateLanguageImportConfig


@dataclass(frozen=True)
class LanguageItemRequest:
    """Request used to enrich one generic item with `.lang`."""

    record: SpecRecord[object]
    runtime: LanguageRuntime


class LanguageTypeSourceKind(StrEnum):
    """Normalized source kind for language type creation."""

    PRIMITIVE = "primitive"
    ENUM = "enum"
    COMPOSITE = "composite"
    MODEL = "model"
    DTO = "dto"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LanguageTypeFacts:
    """Typed facts needed to create a language type annotation."""

    source_kind: LanguageTypeSourceKind
    primitive_type: str | None = None
    primitive_format: str | None = None
    name: SpecName | None = None
    ref: SpecRef | None = None


@dataclass(frozen=True)
class LanguageFieldRequest:
    """Request used to enrich one field-like item with `.lang`."""

    name: SpecName
    type_facts: LanguageTypeFacts
    flags: TemplateFieldFlags
    runtime: LanguageRuntime


@dataclass(frozen=True)
class LanguageOperationRequest:
    """Request used to enrich one operation-like item with `.lang`."""

    record: SpecRecord[object]
    runtime: LanguageRuntime


@dataclass(frozen=True)
class LanguageRouteRequest:
    """Request used to enrich one route-like item with `.lang`."""

    record: SpecRecord[object]
    runtime: LanguageRuntime


@dataclass(frozen=True)
class LanguageTypeRequest:
    """Request used to create one language type annotation."""

    facts: LanguageTypeFacts
    is_required: bool = False
    is_nullable: bool = False
    is_array: bool = False
    is_dynamic: bool = False
    is_void: bool = False


@dataclass(frozen=True)
class LanguageImportTarget:
    """One dependency target used to create imports for a file."""

    symbol: str
    target_path: Path
    source_path: Path
    is_type_only: bool = False
    alias: str | None = None


@dataclass(frozen=True)
class LanguageImportRequest:
    """Request used to create file-level imports."""

    source_path: Path
    targets: tuple[LanguageImportTarget, ...]
    runtime: LanguageRuntime


@dataclass(frozen=True)
class LanguageExportTarget:
    """One emitted symbol used to create exports for a file/barrel."""

    symbol: str
    target_path: Path
    source_path: Path
    alias: str | None = None


@dataclass(frozen=True)
class LanguageExportRequest:
    """Request used to create file-level exports."""

    source_path: Path
    targets: tuple[LanguageExportTarget, ...]
    strategy: LanguageExportStrategy
    runtime: LanguageRuntime


class LanguageAdapter(Protocol):
    """Required interface every Codepotx language adapter must implement."""

    key: str

    def create_runtime(self, request: LanguageRuntimeRequest) -> LanguageRuntime:
        """Create global language runtime context."""

    def enrich_item(self, request: LanguageItemRequest) -> LanguageItem:
        """Create generic per-item `.lang` context."""

    def enrich_field(self, request: LanguageFieldRequest) -> LanguageField:
        """Create field-level `.lang` context."""

    def enrich_operation(self, request: LanguageOperationRequest) -> LanguageOperation:
        """Create operation-level `.lang` context."""

    def enrich_route(self, request: LanguageRouteRequest) -> LanguageRoute:
        """Create route-level `.lang` context."""

    def create_type(
        self,
        request: LanguageTypeRequest,
        runtime: LanguageRuntime,
    ) -> LanguageType:
        """Create a language-specific type annotation."""

    def create_imports(
        self,
        request: LanguageImportRequest,
    ) -> tuple[LanguageImport, ...]:
        """Create file-level imports after emission/dependency planning."""

    def create_exports(
        self,
        request: LanguageExportRequest,
    ) -> tuple[LanguageExport, ...]:
        """Create file-level exports for normal files or barrels."""