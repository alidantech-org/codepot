"""TypeScript import planner.

This module builds TypeScript imports for generated-file dependencies.

It does not resolve dependency refs, decide whether dependencies exist, or decide
whether primitives are importable. Those facts are prepared by generic emission.
This planner only converts an already resolved dependency target path into a
TypeScript-safe import statement.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from contracts.template import TemplateDependency, TemplateImport
from emission.imports.base import ImportPlanningContext
from emission.imports.paths import to_posix_path

STYLE_TYPESCRIPT_NAMED = "typescript_named"
STRATEGY_NONE = "none"
STRATEGY_PACKAGE = "package"
STRATEGY_RELATIVE = "relative"

SRC_PREFIX = "src"
TS_EXTENSIONS = {".ts", ".tsx"}


class TypeScriptImportPlanner:
    """Build TypeScript imports for importable generated dependencies."""

    def plan_imports(self, context: ImportPlanningContext) -> tuple[TemplateImport, ...]:
        """Return prepared TypeScript import objects."""
        if context.strategy == STRATEGY_NONE:
            return ()

        package_name = _package_name(context)
        imports: list[TemplateImport] = []

        for dependency in context.dependencies:
            if not _should_import(dependency):
                continue

            target_path = _public_import_target(dependency)
            import_uri = _import_uri(
                context=context,
                target_path=target_path,
                package_name=package_name,
            )
            symbol = _dependency_symbol(dependency)

            imports.append(
                TemplateImport(
                    ref=dependency.ref,
                    label=symbol,
                    path=import_uri,
                    statement=f"import {{ {symbol} }} from '{import_uri}';",
                    style=STYLE_TYPESCRIPT_NAMED,
                    symbols=(symbol,),
                    dependency=dependency,
                )
            )

        return _dedupe_imports(tuple(imports))


def _should_import(dependency: TemplateDependency) -> bool:
    """Return whether a dependency should become a TypeScript import."""
    if not dependency.is_importable:
        return False

    if dependency.is_self:
        return False

    if dependency.relative_path is None:
        return False

    if dependency.target is not None and dependency.target.is_primitive:
        return False

    return dependency.exists


def _package_name(context: ImportPlanningContext) -> str:
    """Return package name from import context metadata."""
    value = getattr(context, "package_name", None)

    if isinstance(value, str) and value.strip():
        return value.strip()

    meta = getattr(context, "meta", None)
    if isinstance(meta, dict):
        value = meta.get("package_name")
        if isinstance(value, str) and value.strip():
            return value.strip()

    raise ValueError("TypeScript import planning requires package_name in ImportPlanningContext.")


def _public_import_target(dependency: TemplateDependency) -> PurePosixPath:
    """Return the concrete TypeScript file to import for a dependency.

    Current TypeScript templates emit concrete implementation files:
    - model.ts
    - dto.ts
    - enum.ts
    - operation.ts

    Therefore imports must point to the concrete file. Do not rewrite to
    index.ts unless matching index.ts barrel templates are emitted.
    """
    if dependency.relative_path is None:
        raise ValueError(f"dependency has no relative path: {dependency.ref}")

    return to_posix_path(dependency.relative_path)


def _import_uri(
    *,
    context: ImportPlanningContext,
    target_path: PurePosixPath,
    package_name: str,
) -> str:
    """Build TypeScript import URI for the selected strategy."""
    strategy = context.strategy

    if strategy in {"", STRATEGY_PACKAGE}:
        return _package_import_uri(target_path, package_name)

    if strategy == STRATEGY_RELATIVE:
        return _relative_import_uri(
            current_path=to_posix_path(context.current_file.relative_path),
            target_path=target_path,
        )

    raise ValueError(f"Unsupported TypeScript import strategy: {strategy}")


def _package_import_uri(target_path: PurePosixPath, package_name: str) -> str:
    """Build package import URI from an output-relative path."""
    parts = target_path.parts

    if parts and parts[0] == SRC_PREFIX:
        parts = parts[1:]

    if not parts:
        raise ValueError(f"Cannot build TypeScript package import for empty path: {target_path}")

    uri = f"{package_name}/{'/'.join(parts)}"
    return _strip_ts_extension(uri)


def _relative_import_uri(
    *,
    current_path: PurePosixPath,
    target_path: PurePosixPath,
) -> str:
    """Build relative TypeScript import URI with POSIX separators."""
    import posixpath

    current_dir = current_path.parent.as_posix() or "."
    relative = posixpath.relpath(target_path.as_posix(), start=current_dir)
    relative = relative.replace("\\", "/")

    if not relative.startswith("."):
        relative = f"./{relative}"

    return _strip_ts_extension(relative)


def _strip_ts_extension(value: str) -> str:
    """Remove .ts/.tsx suffix from TypeScript import URIs."""
    path = PurePosixPath(value)

    if path.suffix in TS_EXTENSIONS:
        stripped = path.with_suffix("").as_posix()
        if value.startswith("./") and not stripped.startswith("."):
            return f"./{stripped}"
        return stripped

    return value


def _dependency_symbol(dependency: TemplateDependency) -> str:
    """Return the TypeScript symbol name for a dependency."""
    if dependency.target is not None and dependency.target.name is not None:
        return str(dependency.target.name.pascal.o)

    fallback = dependency.ref.rsplit("/", 1)[-1].strip()
    if not fallback:
        raise ValueError(
            f"Cannot determine TypeScript import symbol for dependency: {dependency.ref}"
        )

    return fallback


def _dedupe_imports(imports: tuple[TemplateImport, ...]) -> tuple[TemplateImport, ...]:
    """Deduplicate imports by URI + symbols."""
    seen: set[tuple[str, tuple[str, ...]]] = set()
    unique: list[TemplateImport] = []

    for item in imports:
        key = (item.path, item.symbols)
        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return tuple(unique)
