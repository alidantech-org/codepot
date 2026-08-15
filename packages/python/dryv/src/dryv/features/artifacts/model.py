from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Iterator, Mapping, Sequence


class ArtifactError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


class ArtifactStatus(StrEnum):
    RENDER_COMPLETE = "render_complete"


class WriteKind(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    DELETE_MANAGED = "delete_managed"


@dataclass(frozen=True, slots=True)
class ArtifactProvenance:
    semantic_ids: tuple[str, ...] = ()
    pack_id: str | None = None
    selection_key: str | None = None
    template_resource_id: str | None = None
    invocation_id: str | None = None

    def __post_init__(self) -> None:
        if len(self.semantic_ids) != len(set(self.semantic_ids)):
            raise ValueError("artifact provenance semantic ids must be unique")


@dataclass(frozen=True, slots=True)
class GeneratedArtifact:
    artifact_id: str
    path: str
    logical_output_id: str
    content: bytes
    content_hash: str
    ownership_id: str
    provenance: ArtifactProvenance = ArtifactProvenance()
    dependencies: tuple[str, ...] = ()
    status: ArtifactStatus = ArtifactStatus.RENDER_COMPLETE

    def __post_init__(self) -> None:
        _require_identity("artifact id", self.artifact_id)
        _require_identity("logical output id", self.logical_output_id)
        _require_identity("ownership id", self.ownership_id)
        _safe_path(self.path)
        _require_hash(self.content_hash)
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("artifact dependencies must be unique")


@dataclass(frozen=True, slots=True)
class ManagedOutput:
    path: str
    content_hash: str
    ownership_id: str
    artifact_id: str

    def __post_init__(self) -> None:
        _safe_path(self.path)
        _require_hash(self.content_hash)
        _require_identity("ownership id", self.ownership_id)
        _require_identity("artifact id", self.artifact_id)


@dataclass(frozen=True, slots=True)
class ManagedOutputManifest:
    outputs: tuple[ManagedOutput, ...] = ()
    version: int = 1

    def __post_init__(self) -> None:
        if self.version != 1:
            raise ValueError("unsupported managed-output manifest version")
        paths = tuple(item.path for item in self.outputs)
        if tuple(sorted(paths)) != paths or len(paths) != len(set(paths)):
            raise ValueError("managed outputs must be sorted by unique path")

    def by_path(self) -> dict[str, ManagedOutput]:
        return {item.path: item for item in self.outputs}


@dataclass(frozen=True, slots=True)
class ProjectPathState:
    path: str
    exists: bool
    content_hash: str | None = None

    def __post_init__(self) -> None:
        _safe_path(self.path)
        if self.exists and self.content_hash is None:
            raise ValueError("existing project path state requires a content hash")
        if not self.exists and self.content_hash is not None:
            raise ValueError("missing project path state cannot have a content hash")
        if self.content_hash is not None:
            _require_hash(self.content_hash)


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    paths: tuple[ProjectPathState, ...]

    def __post_init__(self) -> None:
        values = tuple(item.path for item in self.paths)
        if tuple(sorted(values)) != values or len(values) != len(set(values)):
            raise ValueError("project snapshot paths must be sorted and unique")

    def by_path(self) -> dict[str, ProjectPathState]:
        return {item.path: item for item in self.paths}


@dataclass(frozen=True, slots=True)
class WriteInstruction:
    kind: WriteKind
    path: str
    ownership_id: str
    artifact_id: str | None
    expected_previous_hash: str | None
    new_content_hash: str | None
    reason: str
    provenance: ArtifactProvenance = ArtifactProvenance()

    def __post_init__(self) -> None:
        _safe_path(self.path)
        _require_identity("ownership id", self.ownership_id)
        if self.artifact_id is not None:
            _require_identity("artifact id", self.artifact_id)
        if self.expected_previous_hash is not None:
            _require_hash(self.expected_previous_hash)
        if self.new_content_hash is not None:
            _require_hash(self.new_content_hash)
        if not self.reason or self.reason.strip() != self.reason:
            raise ValueError("write instruction reason must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class ArtifactClassification:
    artifacts: tuple[GeneratedArtifact, ...]
    instructions: tuple[WriteInstruction, ...]
    next_manifest: ManagedOutputManifest
    render_complete: bool = True

    def instruction_for(self, path: str) -> WriteInstruction | None:
        return next((item for item in self.instructions if item.path == path), None)


@dataclass(frozen=True, slots=True)
class ArtifactChunk:
    artifact_id: str
    offset: int
    content: bytes
    final: bool


class ArtifactFeature:
    """Classify rendered artifacts without mutating the Project Client filesystem."""

    def classify(
        self,
        artifacts: Sequence[GeneratedArtifact],
        *,
        previous: ManagedOutputManifest = ManagedOutputManifest(),
        snapshot: ProjectSnapshot,
    ) -> ArtifactClassification:
        ordered = tuple(sorted(artifacts, key=lambda item: (item.path, item.artifact_id)))
        artifact_paths = tuple(item.path for item in ordered)
        artifact_ids = tuple(item.artifact_id for item in ordered)
        if len(artifact_paths) != len(set(artifact_paths)):
            raise ArtifactError("ARTIFACT_DUPLICATE_PATH", "generated artifact paths must be unique")
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ArtifactError("ARTIFACT_DUPLICATE_ID", "generated artifact ids must be unique")

        previous_by_path = previous.by_path()
        observed = snapshot.by_path()
        required_paths = set(artifact_paths) | set(previous_by_path)
        missing_observations = sorted(required_paths - set(observed))
        if missing_observations:
            raise ArtifactError(
                "ARTIFACT_OBSERVATION_REQUIRED",
                f"project client did not report path state for {missing_observations[0]!r}",
                path=missing_observations[0],
            )

        instructions: list[WriteInstruction] = []
        next_outputs: list[ManagedOutput] = []
        current_by_path = {item.path: item for item in ordered}

        for artifact in ordered:
            old = previous_by_path.get(artifact.path)
            state = observed[artifact.path]
            if old is None:
                if state.exists:
                    raise ArtifactError(
                        "ARTIFACT_UNMANAGED_COLLISION",
                        f"refusing to classify generated output over unowned path {artifact.path!r}",
                        path=artifact.path,
                    )
                kind = WriteKind.CREATE
                expected = None
                reason = "planned artifact does not exist in the project snapshot"
            else:
                if old.ownership_id != artifact.ownership_id:
                    raise ArtifactError(
                        "ARTIFACT_OWNERSHIP_MISMATCH",
                        f"managed output ownership changed for {artifact.path!r}",
                        path=artifact.path,
                    )
                if not state.exists:
                    kind = WriteKind.CREATE
                    expected = None
                    reason = "previously managed output is missing and will be recreated"
                elif state.content_hash != old.content_hash:
                    raise ArtifactError(
                        "ARTIFACT_USER_MODIFIED",
                        f"previously managed output {artifact.path!r} differs from its recorded hash",
                        path=artifact.path,
                    )
                elif artifact.content_hash == old.content_hash:
                    kind = WriteKind.UNCHANGED
                    expected = old.content_hash
                    reason = "generated content matches the previously managed output"
                else:
                    kind = WriteKind.UPDATE
                    expected = old.content_hash
                    reason = "generated content changed from the previously managed output"

            instructions.append(
                WriteInstruction(
                    kind=kind,
                    path=artifact.path,
                    ownership_id=artifact.ownership_id,
                    artifact_id=artifact.artifact_id,
                    expected_previous_hash=expected,
                    new_content_hash=artifact.content_hash,
                    reason=reason,
                    provenance=artifact.provenance,
                )
            )
            next_outputs.append(
                ManagedOutput(
                    artifact.path,
                    artifact.content_hash,
                    artifact.ownership_id,
                    artifact.artifact_id,
                )
            )

        for path, old in sorted(previous_by_path.items()):
            if path in current_by_path:
                continue
            state = observed[path]
            if not state.exists:
                continue
            if state.content_hash != old.content_hash:
                raise ArtifactError(
                    "ARTIFACT_USER_MODIFIED_STALE",
                    f"stale managed output {path!r} was modified after the recorded build",
                    path=path,
                )
            instructions.append(
                WriteInstruction(
                    kind=WriteKind.DELETE_MANAGED,
                    path=path,
                    ownership_id=old.ownership_id,
                    artifact_id=old.artifact_id,
                    expected_previous_hash=old.content_hash,
                    new_content_hash=None,
                    reason="previously managed output is no longer planned",
                )
            )

        next_manifest = ManagedOutputManifest(tuple(sorted(next_outputs, key=lambda item: item.path)))
        return ArtifactClassification(
            artifacts=ordered,
            instructions=tuple(sorted(instructions, key=lambda item: (item.path, item.kind.value))),
            next_manifest=next_manifest,
            render_complete=True,
        )

    def stream_artifact(
        self,
        artifact: GeneratedArtifact,
        *,
        chunk_size: int = 64 * 1024,
    ) -> Iterator[ArtifactChunk]:
        if chunk_size < 1:
            raise ValueError("artifact stream chunk_size must be positive")
        if not artifact.content:
            yield ArtifactChunk(artifact.artifact_id, 0, b"", True)
            return
        offset = 0
        while offset < len(artifact.content):
            chunk = artifact.content[offset : offset + chunk_size]
            offset_next = offset + len(chunk)
            yield ArtifactChunk(
                artifact_id=artifact.artifact_id,
                offset=offset,
                content=chunk,
                final=offset_next == len(artifact.content),
            )
            offset = offset_next


def _safe_path(path: str) -> None:
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    if (
        not normalized
        or normalized.startswith("/")
        or ":" in parts[0]
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ArtifactError(
            "ARTIFACT_PATH",
            f"artifact paths must be normalized project-relative paths: {path!r}",
            path=path,
        )


def _require_identity(label: str, value: str) -> None:
    if not value or value.strip() != value:
        raise ValueError(f"{label} must be a non-empty trimmed string")


def _require_hash(value: str) -> None:
    if not value or value.strip() != value:
        raise ValueError("content hash identity must be non-empty and trimmed")


__all__ = [
    "ArtifactChunk",
    "ArtifactClassification",
    "ArtifactError",
    "ArtifactFeature",
    "ArtifactProvenance",
    "ArtifactStatus",
    "GeneratedArtifact",
    "ManagedOutput",
    "ManagedOutputManifest",
    "ProjectPathState",
    "ProjectSnapshot",
    "WriteInstruction",
    "WriteKind",
]
