"""Python adapter utility helpers."""

from __future__ import annotations

import posixpath
from pathlib import Path

from archives.codepot.src.languages.python.constants import PYTHON_SOURCE_EXTENSIONS


def remove_known_extension(path: str) -> str:
    """Remove a known Python source extension."""

    for suffix in PYTHON_SOURCE_EXTENSIONS:
        if path.endswith(suffix):
            return path[: -len(suffix)]

    return path


def relative_module_path(
    source_path: Path,
    target_path: Path,
    *,
    include_extension: bool,
) -> str:
    """Create normalized Python relative module path text."""

    source_dir = source_path.parent.as_posix()
    target = target_path.as_posix()
    module = posixpath.relpath(target, source_dir)

    if not include_extension:
        module = remove_known_extension(module)

    return module


def dotted_module_path(path: str) -> str:
    """Convert a path-like module into a Python dotted module."""

    path = remove_known_extension(path.strip("/"))
    return ".".join(part for part in path.split("/") if part)
