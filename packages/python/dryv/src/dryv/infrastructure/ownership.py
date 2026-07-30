from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dryv.generation.models import MemoryOutput
from dryv.ports.writers import (
    ManagedWriteChange,
    ManagedWriteKind,
    ManagedWriteReport,
)

_STATE_PATH = ".dryv/generation-state.json"
_STATE_FORMAT = "dryv-generation-state/v1"


@dataclass(frozen=True, slots=True)
class GenerationState:
    artifacts: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        paths = tuple(path for path, _ in self.artifacts)
        if tuple(sorted(paths)) != paths or len(paths) != len(set(paths)):
            raise ValueError("generation state artifacts must be sorted by unique path")
        for path, digest in self.artifacts:
            _safe_relative(path)
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("generation state digests must be lowercase SHA-256 values")

    def digest_for(self, path: str) -> str | None:
        return dict(self.artifacts).get(path)

    def to_json(self) -> bytes:
        document = {
            "artifacts": [{"path": path, "sha256": digest} for path, digest in self.artifacts],
            "format": _STATE_FORMAT,
        }
        return (
            json.dumps(document, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"
        ).encode("utf-8")

    @classmethod
    def from_bytes(cls, content: bytes) -> GenerationState:
        try:
            document = json.loads(content.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("generation state is not valid UTF-8 JSON") from exc
        if not isinstance(document, dict) or set(document) != {"artifacts", "format"}:
            raise ValueError("generation state has an invalid root shape")
        if document["format"] != _STATE_FORMAT:
            raise ValueError("generation state format is unsupported")
        raw = document["artifacts"]
        if not isinstance(raw, list):
            raise ValueError("generation state artifacts must be an array")
        artifacts: list[tuple[str, str]] = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                raise ValueError(f"generation state artifact {index} is invalid")
            path = item["path"]
            digest = item["sha256"]
            if not isinstance(path, str) or not isinstance(digest, str):
                raise ValueError(f"generation state artifact {index} values must be strings")
            artifacts.append((path, digest))
        return cls(tuple(sorted(artifacts)))


class ManagedFilesystemWriter:
    """Transactionally maintain generated files without overwriting unmanaged work."""

    def write(self, output: MemoryOutput, root: str | Path) -> ManagedWriteReport:
        destination_root = Path(root).resolve()
        destination_root.mkdir(parents=True, exist_ok=True)
        previous = _load_state(destination_root)
        previous_paths = dict(previous.artifacts)
        current = {
            artifact.path: (artifact.content, _digest(artifact.content))
            for artifact in output.artifacts
        }

        changes: list[ManagedWriteChange] = []
        operations: list[tuple[str, Path, bytes | None]] = []

        for path in sorted(current):
            content, digest = current[path]
            destination = _destination(destination_root, path)
            old_digest = previous_paths.get(path)
            if destination.exists():
                if not destination.is_file():
                    raise ValueError(f"managed output destination is not a file: {path}")
                existing = destination.read_bytes()
                existing_digest = _digest(existing)
                if existing == content:
                    changes.append(ManagedWriteChange(path, ManagedWriteKind.LEAVE))
                    continue
                if old_digest is None:
                    raise ValueError(
                        f"WRITE_UNMANAGED_COLLISION: refusing to overwrite unmanaged file {path!r}"
                    )
                if existing_digest != old_digest:
                    raise ValueError(
                        f"WRITE_PROTECTED_MODIFICATION: managed file {path!r} was edited manually"
                    )
                changes.append(ManagedWriteChange(path, ManagedWriteKind.CHANGE))
            else:
                changes.append(ManagedWriteChange(path, ManagedWriteKind.CREATE))
            operations.append(("write", destination, content))

        next_state = dict((path, digest) for path, (_, digest) in current.items())
        for path, old_digest in previous.artifacts:
            if path in current:
                continue
            destination = _destination(destination_root, path)
            if not destination.exists():
                continue
            if not destination.is_file() or _digest(destination.read_bytes()) != old_digest:
                changes.append(
                    ManagedWriteChange(
                        path,
                        ManagedWriteKind.PROTECT,
                        "stale managed path changed outside Dryv",
                    )
                )
                continue
            operations.append(("delete", destination, None))
            changes.append(ManagedWriteChange(path, ManagedWriteKind.DELETE))

        state = GenerationState(tuple(sorted(next_state.items())))
        operations.append(("write", _destination(destination_root, _STATE_PATH), state.to_json()))
        _commit(destination_root, operations)
        return ManagedWriteReport(tuple(sorted(changes, key=lambda item: item.path)))


def _load_state(root: Path) -> GenerationState:
    path = _destination(root, _STATE_PATH)
    if not path.exists():
        return GenerationState()
    if not path.is_file():
        raise ValueError("generation state path is not a regular file")
    return GenerationState.from_bytes(path.read_bytes())


def _commit(root: Path, operations: list[tuple[str, Path, bytes | None]]) -> None:
    staging = Path(tempfile.mkdtemp(prefix=".dryv-owned-", dir=root.parent))
    backups = staging / "backups"
    writes = staging / "writes"
    committed: list[tuple[str, Path, Path | None]] = []
    try:
        for operation, destination, content in operations:
            relative = destination.relative_to(root)
            backup: Path | None = None
            if destination.exists():
                backup = backups / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, backup)
            if operation == "write":
                assert content is not None
                staged = writes / relative
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(content)
                destination.parent.mkdir(parents=True, exist_ok=True)
                try:
                    os.replace(staged, destination)
                except Exception:
                    if backup is not None and backup.exists():
                        os.replace(backup, destination)
                    raise
            elif operation != "delete":
                raise ValueError(f"unknown managed write operation {operation!r}")
            committed.append((operation, destination, backup))
    except Exception:
        for _, destination, backup in reversed(committed):
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
        shutil.rmtree(staging, ignore_errors=True)


def _destination(root: Path, path: str) -> Path:
    relative = _safe_relative(path)
    destination = root.joinpath(*relative.parts)
    try:
        destination.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError("managed output path escapes destination root") from exc
    return destination


def _safe_relative(path: str) -> PurePosixPath:
    if not path or path.startswith("/") or "\\" in path:
        raise ValueError("managed output paths must be POSIX-relative")
    value = PurePosixPath(path)
    if any(part in {"", ".", ".."} for part in value.parts):
        raise ValueError("managed output paths cannot contain dot or traversal segments")
    return value


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate generation state key {key!r}")
        result[key] = value
    return result
