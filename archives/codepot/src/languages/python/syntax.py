"""Python syntax builders.

This module is the single place where Python syntax strings are created.
Other Python adapter modules should call these helpers instead of manually
building syntax with inline f-strings.
"""

from __future__ import annotations

from pathlib import Path

from archives.codepot.src.languages.python.constants import PY_NONE
from archives.codepot.src.languages.python.utils import (
    dotted_module_path,
    relative_module_path,
    remove_known_extension,
)


def alias(left: str, right: str | None) -> str:
    """Create Python alias syntax ('name' or 'name as alias').

    If right is falsy the alias clause is omitted entirely.
    """
    if not right:
        return left

    return f"{left} as {right}"


def nullable(annotation: str) -> str:
    """Create a Python nullable annotation ('T | None')."""
    return union((annotation, PY_NONE))


def array(annotation: str) -> str:
    """Create a Python list annotation ('list[T]')."""
    return f"list[{annotation}]"


def union(values: tuple[str, ...] | list[str]) -> str:
    """Create a Python union annotation ('A | B | C').

    Duplicate entries are removed while preserving original order,
    so the first occurrence of each type wins.
    """
    # dict.fromkeys gives ordered deduplication without a manual loop.
    unique = list(dict.fromkeys(values))
    return " | ".join(unique)


def import_line(*, module: str, symbols: tuple[str, ...]) -> str:
    """Create a Python from-import line ('from module import a, b')."""
    return f"from {module} import {', '.join(symbols)}"


def import_module_line(*, module: str, alias_name: str | None = None) -> str:
    """Create a Python module import line ('import module' or 'import module as alias')."""
    if alias_name:
        return f"import {module} as {alias_name}"

    return f"import {module}"


def export_all_assignment(symbols: tuple[str, ...]) -> str:
    """Create a Python __all__ assignment.

    Uses a tuple literal so a trailing comma is always valid, even for
    a single symbol.

    Example:
        symbols=("Foo", "Bar") → "__all__ = ('Foo', 'Bar',)"
    """
    items = ", ".join(repr(symbol) for symbol in symbols)
    return f"__all__ = ({items},)"


def join_path_tokens(tokens: tuple[str, ...] | list[str]) -> str:
    """Join module/path tokens using Python's dotted package separator.

    Both '/' and '.' are stripped from token edges before joining so
    that callers can pass either POSIX path segments or dotted module
    fragments interchangeably without producing double separators.

    Empty/falsy tokens are dropped silently.
    """
    cleaned = [token.strip("/.") for token in tokens if token]
    return ".".join(cleaned)


def strip_root_prefix(path: str, root: str | None) -> str:
    """Strip a configured source root prefix from a module path.

    Used so that an alias or package name can replace the root folder
    (e.g. root="src" turns "src/models/user" into "models/user").

    Returns:
        - Empty string if path equals the root exactly.
        - The path unchanged if root is None, empty, or not a prefix.
        - The path with the root prefix (and its trailing slash) removed.
    """
    if not root:
        return path

    # Normalize away leading/trailing slashes for consistent comparison.
    normalized_root = root.strip("/")
    if not normalized_root:
        return path

    # Exact match — the target *is* the root; no suffix remains.
    if path == normalized_root:
        return ""

    # Guard against partial segment matches (e.g. root="src" must not
    # strip "srctypes/foo").
    prefix = f"{normalized_root}/"
    if path.startswith(prefix):
        return path[len(prefix) :]

    return path


def maybe_without_extension(path: str, *, include_extension: bool) -> str:
    """Conditionally strip a known source extension from a module path.

    Python imports never include file extensions; this exists for
    symmetry with configurations that explicitly control extension
    inclusion.
    """
    if include_extension:
        return path

    return remove_known_extension(path)


def alias_module_path(
    *,
    alias_name: str,
    target_path: Path,
    root: str | None,
    include_extension: bool,
) -> str:
    """Build an alias/root-based Python module path (e.g. 'myalias.models.user').

    The root is stripped first so the alias substitutes it cleanly, then
    the extension is removed before converting to dotted notation.

    Example:
        alias_name="myapp", root="src", target="src/models/user.py"
        → "myapp.models.user"
    """
    target = strip_root_prefix(target_path.as_posix(), root)
    # Extension is stripped before dotted conversion so that
    # remove_known_extension operates on a slash-separated path,
    # which is what it expects.
    target = maybe_without_extension(target, include_extension=include_extension)
    return join_path_tokens((alias_name, dotted_module_path(target)))


def package_module_path(
    *,
    package: str,
    target_path: Path,
    include_extension: bool,
) -> str:
    """Build a package-based Python module path (e.g. 'mypackage.helpers.format').

    Unlike alias paths, no root stripping is applied — the full target
    path is appended after the package name. This assumes the target is
    already relative to the package root.

    Extension is stripped before dotted conversion (consistent with
    alias_module_path) so remove_known_extension sees a slash-separated
    path rather than a dotted one.

    Example:
        package="mypackage", target="helpers/format.py"
        → "mypackage.helpers.format"
    """
    # Strip extension on the POSIX path before converting to dotted notation,
    # keeping the operation order consistent with alias_module_path.
    target = maybe_without_extension(
        target_path.as_posix(), include_extension=include_extension
    )
    return join_path_tokens((package, dotted_module_path(target)))


def relative_import_module_path(
    *,
    source_path: Path,
    target_path: Path,
    include_extension: bool,
) -> str:
    """Build a Python relative module path from source to target.

    Returns a dotted relative path anchored with a leading dot so it is
    valid as a Python relative import (e.g. '.sibling' or '..parent.child').

    Note: this is a best-effort approximation based on file paths alone.
    Accuracy improves when callers supply proper package-root context.

    Example:
        source="src/resources/users/routes.py", target="src/models/user.py"
        → "...models.user"
    """
    module = relative_module_path(
        source_path,
        target_path,
        include_extension=include_extension,
    )

    module = dotted_module_path(module)

    # Ensure the path is explicitly relative. relative_module_path may
    # return a same-directory module without a leading dot.
    if not module.startswith("."):
        module = f".{module}"

    return module
