from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from .diff import ChangeKind, ChangeSet, FileChange


@dataclass(frozen=True, slots=True)
class StagedFile:
    change: FileChange
    staged_path: Path


class StagedChangeSet:
    def __init__(self, changes: ChangeSet, files: tuple[StagedFile, ...], workspace: TemporaryDirectory[str]) -> None:
        self.changes = changes
        self.files = files
        self._workspace = workspace
        self.root = Path(workspace.name)
        self._closed = False

    def __enter__(self) -> StagedChangeSet:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._workspace.cleanup()


def stage_changes(changes: ChangeSet) -> StagedChangeSet:
    if changes.conflicts:
        raise ValueError("cannot stage a ChangeSet containing conflicts")
    workspace = TemporaryDirectory(prefix=".dryv-stage-", dir=changes.root.parent)
    stage_root = Path(workspace.name) / "files"
    stage_root.mkdir(parents=True, exist_ok=True)
    files: list[StagedFile] = []
    try:
        for index, change in enumerate(changes.changes):
            if change.kind not in {ChangeKind.CREATE, ChangeKind.UPDATE}:
                continue
            target = stage_root / f"{index:08d}"
            with change.artifact.open() as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=64 * 1024)
                destination.flush()
            files.append(StagedFile(change, target))
        return StagedChangeSet(changes, tuple(files), workspace)
    except Exception:
        workspace.cleanup()
        raise


__all__ = ["StagedChangeSet", "StagedFile", "stage_changes"]
