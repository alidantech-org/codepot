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
    """Output for one task from ``Codepotg.yaml``."""

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
    """Output from ``Codepotg.yaml``-driven generation."""

    config_path: Path
    dry_run: bool = False
    tasks: list[GenerateTaskOutput] = field(default_factory=list)
    diagnostics: list[RuntimeDiagnostic] = field(default_factory=list)


@dataclass(frozen=True)
class JsonlOutput:
    """Output from indexed JSONL compilation."""

    input_path: Path
    output_path: Path
    reused: bool = False
    records: int = 0
    definitions: int = 0
    mentions: int = 0
    dependencies: int = 0
    files: list[Path] = field(default_factory=list)
    record_queue_high_water: int = 0
    pending_bytes_high_water: int = 0
    event_queue_high_water: int = 0
    record_waits: int = 0
    event_waits: int = 0


@dataclass(frozen=True)
class PathFolderSummary:
    """Resolved legacy folder recipe from paths.yaml/paths.yml."""

    name: str
    select: str
    alias: str
    mode: str
    lifecycle: str | None
    parts: tuple[str, ...]
    description: str = "-"


@dataclass(frozen=True)
class PathSelectionSummary:
    """Resolved named source selection."""

    name: str
    select: str
    alias: str
    scope: str
    description: str = "-"


@dataclass(frozen=True)
class PathProviderSummary:
    """Resolved explicit dependency provider edge."""

    purpose: str
    source: str


@dataclass(frozen=True)
class PathEmissionSummary:
    """Resolved direct output emission."""

    name: str
    selection: str
    template: str
    output: tuple[str, ...]
    providers: tuple[PathProviderSummary, ...] = ()
    provides: tuple[str, ...] = ()
    lifecycle: str | None = None
    description: str = "-"


@dataclass(frozen=True)
class PathBarrelSummary:
    """Resolved aggregate barrel output."""

    name: str
    template: str
    output: tuple[str, ...]
    exports: tuple[str, ...]
    scope: str
    alias: str
    lifecycle: str | None = None
    description: str = "-"


@dataclass(frozen=True)
class PathsOutput:
    """Resolved template paths configuration."""

    template_root: Path
    config_path: Path | None
    template_extension: str
    strip_template_extension: bool
    allow_raw_files: bool
    import_strategy: str
    folders: list[PathFolderSummary] = field(default_factory=list)
    selections: list[PathSelectionSummary] = field(default_factory=list)
    emissions: list[PathEmissionSummary] = field(default_factory=list)
    barrels: list[PathBarrelSummary] = field(default_factory=list)
    default_lifecycle: str = "managed"
    managed_roots: tuple[str, ...] = ()
    immutable_roots: tuple[str, ...] = ()
    protected_roots: tuple[str, ...] = ()
    clean_roots: tuple[str, ...] = ()
