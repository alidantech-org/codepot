from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from codepotg.diagnostics import Diagnostics
from codepotg.domain.generation import SelectionContext


class PackFileKind(StrEnum):
    TEMPLATE = "template"
    STATIC = "static"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class DiscoveredPackFile:
    pack_path: str
    kind: PackFileKind
    content: bytes
    engine_id: str | None = None
    engine_suffix: str | None = None
    target_id: str | None = None
    target_suffix: str | None = None
    selection_key: str | None = None


@dataclass(frozen=True, slots=True)
class ModuleDescriptor:
    selection_key: str
    artifact_path: str
    specifier: str
    symbols: tuple[str, ...] = ()
    semantic_id: str | None = None


@dataclass(frozen=True, slots=True)
class ModuleCollection:
    modules: tuple[ModuleDescriptor, ...] = ()


@dataclass(frozen=True, slots=True)
class ArtifactPlan:
    id: str
    pack_instance: str
    pack_id: str
    selection_key: str | None
    template_id: str
    output_path: str
    kind: PackFileKind
    context: SelectionContext | None = None
    semantic_id: str | None = None
    group_id: str | None = None
    engine_id: str | None = None
    target_id: str | None = None
    symbols: tuple[str, ...] = ()
    imports: tuple[tuple[str, ModuleCollection], ...] = ()
    exports: tuple[tuple[str, ModuleCollection], ...] = ()
    partials: tuple[tuple[str, str], ...] = ()
    content: bytes | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.output_path or not self.template_id:
            raise ValueError("artifact plans require ids, template ids, and output paths")
        for label, values in (
            ("imports", self.imports),
            ("exports", self.exports),
            ("partials", self.partials),
        ):
            keys = tuple(key for key, _ in values)
            if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
                raise ValueError(f"artifact {label} must be sorted by unique key")
        if self.kind is PackFileKind.TEMPLATE and self.engine_id is None:
            raise ValueError("template artifacts require a template engine id")
        if self.kind is PackFileKind.STATIC and self.content is None:
            raise ValueError("static artifacts require content")


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    project_name: str
    artifacts: tuple[ArtifactPlan, ...]
    diagnostics: Diagnostics = field(default_factory=Diagnostics)

    def __post_init__(self) -> None:
        paths = tuple(item.output_path for item in self.artifacts)
        ids = tuple(item.id for item in self.artifacts)
        if len(paths) != len(set(paths)):
            raise ValueError("generation plans cannot contain output path collisions")
        if len(ids) != len(set(ids)):
            raise ValueError("generation plans cannot contain duplicate artifact ids")

    @property
    def ready(self) -> bool:
        return not self.diagnostics.has_errors


@dataclass(frozen=True, slots=True)
class GeneratedArtifact:
    id: str
    path: str
    content: bytes
    target_id: str | None
    template_id: str
    semantic_id: str | None = None

    def text(self) -> str:
        return self.content.decode("utf-8")


@dataclass(frozen=True, slots=True)
class MemoryOutput:
    artifacts: tuple[GeneratedArtifact, ...]

    def __post_init__(self) -> None:
        if tuple(sorted(self.artifacts, key=lambda item: item.path)) != self.artifacts:
            raise ValueError("memory output artifacts must be sorted by path")

    def get(self, path: str) -> GeneratedArtifact | None:
        return next((item for item in self.artifacts if item.path == path), None)


@dataclass(frozen=True, slots=True)
class GenerationData:
    plan: GenerationPlan
    output: MemoryOutput | None = None
