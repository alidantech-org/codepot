"""Dart syntax builders.

This module is the single place where Dart syntax strings are created.
Other Dart adapter modules should call these helpers instead of manually
building syntax with inline f-strings.
"""

from __future__ import annotations

from pathlib import Path

from archives.codepot.src.languages.dart.utils import (
    ensure_dart_extension,
    relative_module_path,
    remove_known_extension,
)


def quoted(value: str) -> str:
    """Create a Dart single-quoted string literal."""

    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def alias(left: str, right: str | None) -> str:
    """Create Dart alias-like text for display contexts.

    Dart imports do not support per-symbol aliasing. Import aliases are library
    prefixes and should be handled at the import-line level later.
    """

    if not right:
        return left

    return f"{left} as {right}"


def nullable(annotation: str) -> str:
    """Create a Dart nullable annotation."""

    if annotation.endswith("?"):
        return annotation

    return f"{annotation}?"


def array(annotation: str) -> str:
    """Create a Dart list annotation."""

    return f"List<{annotation}>"


def import_line(*, module: str, symbols: tuple[str, ...] = ()) -> str:
    """Create a Dart import line."""

    if symbols:
        visible = ", ".join(symbols)
        return f"import {quoted(module)} show {visible};"

    return f"import {quoted(module)};"


def export_line(*, module: str, symbols: tuple[str, ...] = ()) -> str:
    """Create a Dart export line."""

    if symbols:
        visible = ", ".join(symbols)
        return f"export {quoted(module)} show {visible};"

    return f"export {quoted(module)};"


def join_path_tokens(tokens: tuple[str, ...] | list[str]) -> str:
    """Join URI/path tokens using Dart URI separator."""

    cleaned = [token.strip("/") for token in tokens if token]
    return "/".join(cleaned)


def strip_root_prefix(path: str, root: str | None) -> str:
    """Strip a configured source root prefix from a module path."""

    if not root:
        return path

    normalized_root = root.strip("/")
    if not normalized_root:
        return path

    if path == normalized_root:
        return ""

    prefix = f"{normalized_root}/"
    if path.startswith(prefix):
        return path[len(prefix) :]

    return path


def maybe_with_extension(path: str, *, include_extension: bool) -> str:
    """Apply Dart URI extension preference."""

    if include_extension:
        return ensure_dart_extension(path)

    return remove_known_extension(path)


def package_module_path(
    *,
    package: str,
    target_path: Path,
    root: str | None,
    include_extension: bool,
) -> str:
    """Create a Dart package import URI."""

    target = strip_root_prefix(target_path.as_posix(), root)
    target = maybe_with_extension(target, include_extension=include_extension)
    return f"package:{join_path_tokens((package, target))}"


def alias_module_path(
    *,
    alias_name: str,
    target_path: Path,
    root: str | None,
    include_extension: bool,
) -> str:
    """Create an alias/root-style Dart URI.

    This is mainly for non-standard template packages. For typical Dart packages,
    prefer ``package_module_path``.
    """

    target = strip_root_prefix(target_path.as_posix(), root)
    target = maybe_with_extension(target, include_extension=include_extension)
    return join_path_tokens((alias_name, target))


def relative_import_module_path(
    *,
    source_path: Path,
    target_path: Path,
    include_extension: bool,
) -> str:
    """Create a relative Dart import/export URI."""

    return relative_module_path(
        source_path,
        target_path,
        include_extension=include_extension,
    )
