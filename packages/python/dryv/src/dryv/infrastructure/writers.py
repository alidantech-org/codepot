from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath

from dryv.generation import MemoryOutput


class WriteKind(StrEnum):
    CREATE = "create"
    CHANGE = "change"
    LEAVE = "leave"


@dataclass(frozen=True, slots=True)
class WriteChange:
    path: str
    kind: WriteKind


@dataclass(frozen=True, slots=True)
class WriteReport:
    changes: tuple[WriteChange, ...]

    @property
    def changed(self) -> bool:
        return any(item.kind is not WriteKind.LEAVE for item in self.changes)


class TransactionalFilesystemWriter:
    """Stage every artifact and roll back all replacements when commit fails."""

    def write(self, output: MemoryOutput, root: str | Path) -> WriteReport:
        destination_root = Path(root).resolve()
        destination_root.mkdir(parents=True, exist_ok=True)
        staging_root = Path(
            tempfile.mkdtemp(prefix=".dryv-stage-", dir=destination_root.parent)
        )
        content_root = staging_root / "content"
        backup_root = staging_root / "backup"
        changes: list[WriteChange] = []
        committed: list[tuple[Path, Path | None]] = []

        try:
            for artifact in output.artifacts:
                relative = _safe_relative(artifact.path)
                staged = content_root.joinpath(*relative.parts)
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(artifact.content)

            for artifact in output.artifacts:
                relative = _safe_relative(artifact.path)
                destination = destination_root.joinpath(*relative.parts)
                staged = content_root.joinpath(*relative.parts)
                if destination.is_file() and destination.read_bytes() == artifact.content:
                    changes.append(WriteChange(artifact.path, WriteKind.LEAVE))
                    continue

                backup: Path | None = None
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    if not destination.is_file():
                        raise ValueError(
                            f"writer destination is not a regular file: {artifact.path}"
                        )
                    backup = backup_root.joinpath(*relative.parts)
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(destination, backup)
                    kind = WriteKind.CHANGE
                else:
                    kind = WriteKind.CREATE

                try:
                    os.replace(staged, destination)
                except Exception:
                    if backup is not None and backup.exists():
                        os.replace(backup, destination)
                    raise
                committed.append((destination, backup))
                changes.append(WriteChange(artifact.path, kind))

            return WriteReport(tuple(sorted(changes, key=lambda item: item.path)))
        except Exception:
            for destination, backup in reversed(committed):
                try:
                    if destination.exists():
                        destination.unlink()
                    if backup is not None and backup.exists():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(backup, destination)
                except OSError:
                    pass
            raise
        finally:
            shutil.rmtree(staging_root, ignore_errors=True)


def _safe_relative(path: str) -> PurePosixPath:
    if not path or path.startswith("/") or "\\" in path:
        raise ValueError("writer paths must be POSIX-relative")
    value = PurePosixPath(path)
    if any(part in {"", ".", ".."} for part in value.parts):
        raise ValueError("writer paths cannot contain dot or traversal segments")
    return value
