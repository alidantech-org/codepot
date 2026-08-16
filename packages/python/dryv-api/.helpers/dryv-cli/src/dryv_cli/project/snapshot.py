from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath

from .project import ProjectError


@dataclass(frozen=True, slots=True)
class ProjectPathSnapshot:
    path: str
    exists: bool
    content_hash: str | None
    size: int | None


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    root: Path
    paths: tuple[ProjectPathSnapshot, ...]


def snapshot_paths(root: Path, paths: tuple[str, ...]) -> ProjectSnapshot:
    root = root.resolve()
    result: list[ProjectPathSnapshot] = []
    for value in sorted(set(paths)):
        relative = _relative(value)
        target = root.joinpath(*relative.parts)
        resolved = target.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ProjectError("CLI_PATH_ESCAPE", f"path escapes project root: {value!r}", path=value) from exc
        if not target.exists():
            result.append(ProjectPathSnapshot(value, False, None, None))
            continue
        if not target.is_file():
            raise ProjectError("CLI_PATH_TYPE", f"path is not a regular file: {value!r}", path=value)
        content = target.read_bytes()
        result.append(ProjectPathSnapshot(value, True, f"sha256:{sha256(content).hexdigest()}", len(content)))
    return ProjectSnapshot(root, tuple(result))


def _relative(value: str) -> PurePosixPath:
    if not value or value.startswith("/") or "\\" in value:
        raise ProjectError("CLI_PATH_INVALID", f"path must be POSIX-relative: {value!r}", path=value)
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectError("CLI_PATH_INVALID", f"path contains an invalid segment: {value!r}", path=value)
    return path


__all__ = ["ProjectPathSnapshot", "ProjectSnapshot", "snapshot_paths"]
