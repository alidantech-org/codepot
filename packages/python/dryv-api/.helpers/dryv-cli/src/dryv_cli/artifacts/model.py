from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass(frozen=True, slots=True)
class ArtifactProvenance:
    job_id: str
    plan_index: int
    semantic_ids: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    subject_id: str | None = None
    subject_kind: str | None = None
    pack_id: str | None = None
    pack_instance: str | None = None
    template_key: str | None = None
    template_hash: str | None = None


@dataclass(frozen=True, slots=True)
class ReceivedArtifact:
    artifact_id: str
    path: str
    size: int
    content_hash: str
    content_path: Path
    provenance: ArtifactProvenance

    def open(self):
        return self.content_path.open("rb")


class ArtifactSet:
    """Verified generated artifacts backed by one temporary workspace."""

    def __init__(
        self,
        build_id: str,
        plan_hash: str,
        artifacts: tuple[ReceivedArtifact, ...],
        workspace: TemporaryDirectory[str],
    ) -> None:
        self.build_id = build_id
        self.plan_hash = plan_hash
        self.artifacts = artifacts
        self._workspace = workspace
        self._closed = False
        ids = tuple(item.artifact_id for item in artifacts)
        paths = tuple(item.path for item in artifacts)
        if len(ids) != len(set(ids)) or len(paths) != len(set(paths)):
            workspace.cleanup()
            raise ValueError("ArtifactSet artifact ids and paths must be unique")

    def __enter__(self) -> ArtifactSet:
        if self._closed:
            raise RuntimeError("ArtifactSet is closed")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._workspace.cleanup()

    def by_id(self, artifact_id: str) -> ReceivedArtifact | None:
        return next((item for item in self.artifacts if item.artifact_id == artifact_id), None)


__all__ = ["ArtifactProvenance", "ArtifactSet", "ReceivedArtifact"]
