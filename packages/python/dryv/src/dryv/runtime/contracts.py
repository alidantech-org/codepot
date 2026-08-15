from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from dryv.features.artifacts import (
    ArtifactClassification,
    ManagedOutputManifest,
    ProjectSnapshot,
)
from dryv.features.authoring import AuthorRequest, AuthorSession
from dryv.features.cache import CacheMode
from dryv.features.packs import PackTemplateResource
from dryv.features.planning import GenerationPlan, PlanningCandidate
from dryv.features.scheduling import CancellationToken
from dryv.features.templating import RenderSession
from dryv.ir import Contract


class RuntimeBuildError(ValueError):
    def __init__(self, code: str, message: str, *, subject: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.subject = subject


class BuildStatus(StrEnum):
    RENDER_COMPLETE = "render_complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class BuildResource:
    resource_id: str
    media_type: str
    content: bytes
    content_hash: str | None = None

    def __post_init__(self) -> None:
        for label, value in (("resource id", self.resource_id), ("media type", self.media_type)):
            if not value or value.strip() != value:
                raise ValueError(f"{label} must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class BuildPack:
    manifest_document: Mapping[str, object]
    templates: tuple[PackTemplateResource, ...]
    manifest_resource_id: str

    def __post_init__(self) -> None:
        if not self.manifest_resource_id or self.manifest_resource_id.strip() != self.manifest_resource_id:
            raise ValueError("pack manifest resource id must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class AvailableRenderSession:
    session_id: str
    session: RenderSession

    def __post_init__(self) -> None:
        if not self.session_id or self.session_id.strip() != self.session_id:
            raise ValueError("render session id must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class AuthorSourceBuild:
    request: AuthorRequest
    session: AuthorSession


@dataclass(frozen=True, slots=True)
class BuildRequest:
    build_id: str
    resources: tuple[BuildResource, ...]
    planning_candidates: tuple[PlanningCandidate, ...]
    project_document: Mapping[str, object] | None = None
    packs: tuple[BuildPack, ...] = ()
    precompiled_contract: Contract | None = None
    precompiled_ir_resource_id: str | None = None
    author: AuthorSourceBuild | None = None
    render_sessions: tuple[AvailableRenderSession, ...] = ()
    previous_managed_outputs: ManagedOutputManifest = ManagedOutputManifest()
    project_snapshot: ProjectSnapshot = ProjectSnapshot(())
    cache_mode: CacheMode = CacheMode.USE
    commit_cache: bool = True
    cancellation: CancellationToken | None = None

    def __post_init__(self) -> None:
        if not self.build_id or self.build_id.strip() != self.build_id:
            raise ValueError("build id must be non-empty and trimmed")
        sources = sum(
            item is not None
            for item in (self.precompiled_contract, self.precompiled_ir_resource_id, self.author)
        )
        if sources != 1:
            raise ValueError("build requests require exactly one Canonical IR source")
        resource_ids = tuple(item.resource_id for item in self.resources)
        if len(resource_ids) != len(set(resource_ids)):
            raise ValueError("build resource ids must be unique")
        session_ids = tuple(item.session_id for item in self.render_sessions)
        if len(session_ids) != len(set(session_ids)):
            raise ValueError("render session ids must be unique")


@dataclass(frozen=True, slots=True)
class BuildTrace:
    stage: str
    subject: str
    message: str
    details: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.stage or not self.subject or not self.message:
            raise ValueError("build trace requires stage, subject and message")
        if tuple(sorted(self.details)) != self.details:
            raise ValueError("build trace details must be sorted")


@dataclass(frozen=True, slots=True)
class BuildDiagnostic:
    code: str
    message: str
    subject: str | None = None


@dataclass(frozen=True, slots=True)
class BuildCacheStats:
    context_hits: int = 0
    context_misses: int = 0
    render_hits: int = 0
    render_misses: int = 0


@dataclass(frozen=True, slots=True)
class BuildResult:
    build_id: str
    status: BuildStatus
    render_complete: bool
    plan: GenerationPlan | None
    artifacts: ArtifactClassification | None
    trace: tuple[BuildTrace, ...]
    diagnostics: tuple[BuildDiagnostic, ...]
    cache: BuildCacheStats = BuildCacheStats()

    @property
    def success(self) -> bool:
        return self.status is BuildStatus.RENDER_COMPLETE and self.render_complete


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    core_version: str
    features: tuple[str, ...]
    author_protocol_version: int
    render_protocol_version: int


__all__ = [
    "AuthorSourceBuild",
    "AvailableRenderSession",
    "BuildCacheStats",
    "BuildDiagnostic",
    "BuildPack",
    "BuildRequest",
    "BuildResource",
    "BuildResult",
    "BuildStatus",
    "BuildTrace",
    "RuntimeBuildError",
    "RuntimeSnapshot",
]
