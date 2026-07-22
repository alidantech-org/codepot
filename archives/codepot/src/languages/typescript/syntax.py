from pathlib import Path

from archives.codepot.src.languages.typescript.constants import (
    EXPORT_KEYWORD,
    FROM_KEYWORD,
    IMPORT_KEYWORD,
    IMPORT_TYPE_KEYWORD,
    TS_NULL,
)
from archives.codepot.src.languages.typescript.utils import relative_module_path, remove_known_extension


def alias(left: str, right: str | None) -> str:
    """Create TypeScript alias syntax."""

    if not right:
        return left

    return f"{left} as {right}"


def nullable(annotation: str) -> str:
    """Create a TypeScript nullable annotation."""

    return union((annotation, TS_NULL))


def array(annotation: str) -> str:
    """Create a TypeScript array annotation."""

    return f"{annotation}[]"


def union(values: tuple[str, ...] | list[str]) -> str:
    """Create a TypeScript union annotation."""

    unique = list(dict.fromkeys(values))
    return " | ".join(unique)


def import_line(*, module: str, symbols: tuple[str, ...], type_only: bool) -> str:
    """Create a TypeScript named import line."""

    type_keyword = IMPORT_TYPE_KEYWORD if type_only else ""
    rendered_symbols = ", ".join(symbols)
    return f"{IMPORT_KEYWORD}{type_keyword} {{ {rendered_symbols} }} {FROM_KEYWORD} {module!r};"


def export_named_line(*, module: str, symbols: tuple[str, ...]) -> str:
    """Create a TypeScript named export line."""

    rendered_symbols = ", ".join(symbols)
    return f"{EXPORT_KEYWORD} {{ {rendered_symbols} }} {FROM_KEYWORD} {module!r};"


def export_star_line(*, module: str) -> str:
    """Create a TypeScript star export line."""

    return f"{EXPORT_KEYWORD} * {FROM_KEYWORD} {module!r};"


def join_path_tokens(tokens: tuple[str, ...] | list[str]) -> str:
    """Join module/path tokens using TypeScript module separator (/).
    
    Empty strings and None-like falsy tokens are filtered out before
    joining, so callers don't need to pre-clean the token list.
    """
    cleaned = [token.strip("/") for token in tokens if token]
    return "/".join(cleaned)


def strip_root_prefix(path: str, root: str | None) -> str:
    """Strip a configured source root prefix from a module path.

    Used for alias-based imports where the alias replaces the root
    folder (e.g. root="src", alias="@" turns "src/foo" into "@/foo").

    Returns:
        - Empty string if path equals the root exactly.
        - The path unchanged if root is None, empty, or not a prefix.
        - The path with the root prefix (and trailing slash) removed.
    """
    if not root:
        return path

    # Normalize away any leading/trailing slashes for consistent comparison.
    normalized_root = root.strip("/")
    if not normalized_root:
        return path

    # Exact match — the target *is* the root, no suffix remains.
    if path == normalized_root:
        return ""

    # Only strip when the root is a true path segment prefix, not a
    # partial string match (e.g. root="src" must not strip "srctypes/").
    prefix = f"{normalized_root}/"
    if path.startswith(prefix):
        return path[len(prefix):]

    return path


def maybe_without_extension(path: str, *, include_extension: bool) -> str:
    """Conditionally strip a known source extension from a module path.

    TypeScript imports typically omit file extensions; this applies
    `remove_known_extension` only when the import config says to.
    """
    if include_extension:
        return path

    return remove_known_extension(path)


def alias_module_path(
    *,
    alias: str,
    target_path: Path,
    root: str | None,
    include_extension: bool,
) -> str:
    """Build an alias-based module path (e.g. '@/models/user').

    The source root is stripped from the target before the alias is
    prepended, so the alias effectively replaces the root segment.

    Example:
        alias="@", root="src", target="src/models/user.ts"
        → "@/models/user"
    """
    # Strip the root so the alias substitutes it cleanly.
    target = strip_root_prefix(target_path.as_posix(), root)
    module = join_path_tokens((alias, target))
    return maybe_without_extension(module, include_extension=include_extension)


def package_module_path(
    *,
    package: str,
    target_path: Path,
    include_extension: bool,
) -> str:
    """Build a package-based module path (e.g. 'my-lib/helpers/format').

    Unlike alias paths, no root stripping is applied — the full target
    path is appended directly after the package name. This assumes the
    target path is already relative to the package root.

    Example:
        package="my-lib", target="helpers/format.ts"
        → "my-lib/helpers/format"
    """
    module = join_path_tokens((package, target_path.as_posix()))
    return maybe_without_extension(module, include_extension=include_extension)


def relative_import_module_path(
    *,
    source_path: Path,
    target_path: Path,
    include_extension: bool,
) -> str:
    """Build a relative TypeScript import/export path from source to target.

    Delegates to the shared `relative_module_path` utility, which handles
    the './' prefix and '../' traversal logic.

    Example:
        source="src/resources/users/routes.ts", target="src/models/user.ts"
        → "../../models/user"
    """
    return relative_module_path(
        source_path,
        target_path,
        include_extension=include_extension,
    )
