"""TypeScript adapter utility helpers."""

from __future__ import annotations

import posixpath
from pathlib import Path

from archives.codepot.src.languages.typescript.constants import TYPESCRIPT_SOURCE_EXTENSIONS


def remove_known_extension(path: str) -> str:
    """Remove a known TypeScript/JavaScript source extension."""

    for suffix in TYPESCRIPT_SOURCE_EXTENSIONS:
        if path.endswith(suffix):
            return path[: -len(suffix)]

    return path


def relative_module_path(
    source_path: Path,
    target_path: Path,
    *,
    include_extension: bool,
) -> str:
    """Create a normalized relative module path."""

    source_dir = source_path.parent.as_posix()
    target = target_path.as_posix()
    module = posixpath.relpath(target, source_dir)

    if not module.startswith("."):
        module = f"./{module}"

    if not include_extension:
        module = remove_known_extension(module)

    return module
