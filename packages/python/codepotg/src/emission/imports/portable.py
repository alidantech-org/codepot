"""Import planning for Python, Java, C#, Go, and Rust outputs."""

from __future__ import annotations

from pathlib import PurePosixPath

from contracts.template import TemplateDependency, TemplateImport
from emission.imports.base import ImportPlanningContext
from emission.imports.paths import to_posix_path

PORTABLE_SUFFIXES = frozenset({".py", ".java", ".cs", ".go", ".rs"})


class PortableImportPlanner:
    """Build deterministic target imports from resolved virtual output facts."""

    def supports(self, context: ImportPlanningContext) -> bool:
        return context.current_file.suffix in PORTABLE_SUFFIXES

    def plan_imports(
        self,
        context: ImportPlanningContext,
    ) -> tuple[TemplateImport, ...]:
        if context.strategy == "none":
            return ()

        current = to_posix_path(context.current_file.relative_path)
        imports: list[TemplateImport] = []
        seen: set[tuple[str, str]] = set()
        for dependency in context.dependencies:
            if not dependency.is_importable or dependency.relative_path is None:
                continue
            target = to_posix_path(dependency.relative_path)
            if context.current_file.suffix == ".go" and current.parent == target.parent:
                continue
            symbol = _dependency_symbol(dependency)
            planned = _planned_import(
                suffix=context.current_file.suffix,
                current=current,
                target=target,
                symbol=symbol,
                package_name=context.package_name,
                dependency=dependency,
            )
            key = (planned.statement, symbol)
            if key in seen:
                continue
            seen.add(key)
            imports.append(planned)
        return tuple(imports)


def _planned_import(
    *,
    suffix: str,
    current: PurePosixPath,
    target: PurePosixPath,
    symbol: str,
    package_name: str | None,
    dependency: TemplateDependency,
) -> TemplateImport:
    if suffix == ".py":
        path, statement = _python_import(current, target, symbol)
        style = "python_from"
    elif suffix == ".java":
        path = _java_package(target)
        statement = f"import {path}.{symbol};"
        style = "java_import"
    elif suffix == ".cs":
        path = _csharp_namespace(target)
        statement = f"using {path};"
        style = "csharp_using"
    elif suffix == ".go":
        path = _go_package(target, package_name=package_name)
        statement = f'import "{path}"'
        style = "go_import"
    elif suffix == ".rs":
        path = _rust_path(target)
        statement = f"use {path}::{symbol};"
        style = "rust_use"
    else:  # pragma: no cover - guarded by supports()
        raise ValueError(f"Unsupported portable import suffix: {suffix}")

    return TemplateImport(
        ref=dependency.ref,
        label=symbol,
        path=path,
        statement=statement,
        style=style,
        symbols=(symbol,),
        dependency=dependency,
    )


def _python_import(
    current: PurePosixPath,
    target: PurePosixPath,
    symbol: str,
) -> tuple[str, str]:
    current_parent = current.parent.parts
    target_module = target.with_suffix("").parts
    common = 0
    for left, right in zip(current_parent, target_module, strict=False):
        if left != right:
            break
        common += 1
    upward = len(current_parent) - common
    prefix = "." * max(1, upward + 1)
    remainder = ".".join(target_module[common:])
    module = f"{prefix}{remainder}" if remainder else prefix
    return module, f"from {module} import {symbol}"


def _java_package(target: PurePosixPath) -> str:
    parts = _after_marker(target.parent.parts, "java")
    return ".".join(parts) or "generated"


def _csharp_namespace(target: PurePosixPath) -> str:
    parts = _after_marker(target.parent.parts, "package")
    suffix = ".".join(_pascal(part) for part in parts)
    return f"Generated.{suffix}" if suffix else "Generated"


def _go_package(target: PurePosixPath, *, package_name: str | None) -> str:
    module = f"example.com/generated/{package_name or 'generated'}"
    parts = _after_marker(target.parent.parts, "package")
    parent = "/".join(parts)
    return f"{module}/{parent}" if parent else module


def _rust_path(target: PurePosixPath) -> str:
    parts = _after_marker(target.with_suffix("").parts, "src")
    return "::".join(
        ("crate", *(part.replace("-", "_") for part in parts))
    )


def _after_marker(parts: tuple[str, ...], marker: str) -> tuple[str, ...]:
    try:
        index = parts.index(marker)
    except ValueError:
        return parts
    return parts[index + 1 :]


def _dependency_symbol(dependency: TemplateDependency) -> str:
    if dependency.target and dependency.target.name:
        return dependency.target.name.pascal.o
    return dependency.ref.rsplit("/", 1)[-1] or dependency.ref


def _pascal(value: str) -> str:
    words = value.replace("-", "_").split("_")
    return "".join(word[:1].upper() + word[1:] for word in words if word)
