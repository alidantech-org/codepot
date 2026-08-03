"""Dart adapter utility helpers."""

from __future__ import annotations

import posixpath
from pathlib import Path

from archives.codepot.src.languages.dart.constants import DART_SOURCE_EXTENSIONS


def remove_known_extension(path: str) -> str:
    """Remove a known Dart source extension."""

    for suffix in DART_SOURCE_EXTENSIONS:
        if path.endswith(suffix):
            return path[: -len(suffix)]

    return path


def ensure_dart_extension(path: str) -> str:
    """Ensure a path has a Dart source extension."""

    if path.endswith(DART_SOURCE_EXTENSIONS):
        return path

    return f"{path}.dart"


def relative_module_path(
    source_path: Path,
    target_path: Path,
    *,
    include_extension: bool,
) -> str:
    """Create normalized Dart relative import/export URI."""

    source_dir = source_path.parent.as_posix()
    target = target_path.as_posix()
    module = posixpath.relpath(target, source_dir)

    if not module.startswith("."):
        module = f"./{module}"

    module = (
        ensure_dart_extension(module)
        if include_extension
        else remove_known_extension(module)
    )

    return module
