"""POSIX import/link path helpers."""

from __future__ import annotations

import posixpath
from pathlib import Path, PurePosixPath


def to_posix_path(value: Path | PurePosixPath | str) -> PurePosixPath:
    """Normalize a path-like value to a POSIX relative path."""
    return PurePosixPath(str(value).replace("\\", "/"))


def relative_posix_path(*, from_file: PurePosixPath, to_file: PurePosixPath) -> str:
    """Return a POSIX relative path from one emitted file to another."""
    from_dir = from_file.parent.as_posix()
    target = to_file.as_posix()
    return posixpath.relpath(target, start=from_dir or ".").replace("\\", "/")
