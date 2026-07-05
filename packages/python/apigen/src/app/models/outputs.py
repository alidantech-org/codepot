"""Runtime output contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.models.diagnostics import RuntimeDiagnostic


@dataclass(frozen=True)
class ResourceSummary:
    """Detected resource summary."""

    name: str
    path: str = "-"
    operations_count: int = 0


@dataclass(frozen=True)
class UnknownSchemaSummary:
    """Unknown schema summary for inference diagnostics."""

    name: str
    ref: str
    x_codegen_kind: str = "-"
    keys: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AliasSchemaSummary:
    """Alias schema summary for inference diagnostics."""

    name: str
    kind: str
    alias_of: str = "-"
    resource: str = "-"


@dataclass(frozen=True)
class InspectOutput:
    """Output from OpenAPI inspection."""

    input_path: Path
    title: str = "-"
    openapi_version: str = "-"
    api_version: str = "-"
    paths_count: int = 0
    operations_count: int = 0
    schemas_count: int = 0
    responses_count: int = 0
    request_bodies_count: int = 0
    parameters_count: int = 0
    refs_count: int = 0
    component_refs_count: int = 0
    missing_component_refs_count: int = 0
    resources: list[ResourceSummary] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class ValidateOutput:
    """Output from OpenAPI validation."""

    input_path: Path
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class InferOutput:
    """Output from OpenAPI inference."""

    input_path: Path
    output_path: Path | None = None
    graph: Any | None = None
    title: str = "-"
    openapi_version: str = "-"
    api_version: str = "-"
    resources_count: int = 0
    schemas_count: int = 0
    operations_count: int = 0
    dependencies_count: int = 0
    alias_schemas_count: int = 0
    schema_kind_counts: dict[str, int] = field(default_factory=dict)
    unknown_schemas: list[UnknownSchemaSummary] = field(default_factory=list)
    alias_schemas: list[AliasSchemaSummary] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class EmitOutput:
    """Output from code/text emission."""

    input_path: Path
    language: str
    output_path: Path
    dry_run: bool = False
    planned: list[Path] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    unchanged: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    immutable_created: list[Path] = field(default_factory=list)
    immutable_skipped: list[Path] = field(default_factory=list)
    refused: list[Path] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class GenerateTaskOutput:
    """Output for one CodepotFile task."""

    name: str
    input_path: Path
    language: str
    output_path: Path
    template_dir: Path
    dry_run: bool = False
    planned: list[Path] = field(default_factory=list)
    written: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    unchanged: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    immutable_created: list[Path] = field(default_factory=list)
    immutable_skipped: list[Path] = field(default_factory=list)
    refused: list[Path] = field(default_factory=list)
    cleaned: list[Path] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class GenerateOutput:
    """Output from CodepotFile-driven generation."""

    config_path: Path
    dry_run: bool = False
    tasks: list[GenerateTaskOutput] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)
