from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from dryv_cli.artifacts import ArtifactSet, ReceivedArtifact

from .inspect import ExistingFile, ManagedOutput, ManagedState, inspect_file


class ChangeKind(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class FileChange:
    kind: ChangeKind
    artifact: ReceivedArtifact
    existing: ExistingFile
    previous: ManagedOutput | None
    reason: str


@dataclass(frozen=True, slots=True)
class ChangeSet:
    root: Path
    plan_hash: str
    changes: tuple[FileChange, ...]

    @property
    def conflicts(self) -> tuple[FileChange, ...]:
        return tuple(item for item in self.changes if item.kind is ChangeKind.CONFLICT)

    def count(self, kind: ChangeKind) -> int:
        return sum(item.kind is kind for item in self.changes)


def build_change_set(
    root: Path,
    artifacts: ArtifactSet,
    managed: ManagedState,
    *,
    force: bool = False,
) -> ChangeSet:
    root = root.resolve()
    previous = managed.by_path()
    changes: list[FileChange] = []
    for artifact in artifacts.artifacts:
        existing = inspect_file(root, artifact.path)
        prior = previous.get(artifact.path)
        if not existing.exists:
            kind = ChangeKind.CREATE
            reason = "target does not exist"
        elif not existing.regular:
            kind = ChangeKind.CONFLICT
            reason = "target exists but is not a regular file"
        elif existing.content_hash == artifact.content_hash:
            kind = ChangeKind.UNCHANGED
            reason = "local bytes already match generated artifact"
        elif prior is not None and existing.content_hash == prior.content_hash:
            kind = ChangeKind.UPDATE
            reason = "local file still matches previously managed content"
        elif force and existing.regular:
            kind = ChangeKind.UPDATE
            reason = "explicit force allows overwriting a conflicting regular file"
        elif prior is not None:
            kind = ChangeKind.CONFLICT
            reason = "previously managed file was modified locally"
        else:
            kind = ChangeKind.CONFLICT
            reason = "existing file is not managed by Dryv"
        changes.append(FileChange(kind, artifact, existing, prior, reason))
    return ChangeSet(root, artifacts.plan_hash, tuple(sorted(changes, key=lambda item: item.artifact.path)))


__all__ = ["ChangeKind", "ChangeSet", "FileChange", "build_change_set"]
