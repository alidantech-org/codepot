"""Dart import helpers."""

from __future__ import annotations

from pathlib import Path

from archives.codepot.src.contracts.language.imports import (
    LanguageImport,
    LanguageImportKind,
    LanguageImportSymbol,
)
from archives.codepot.src.contracts.language.interface import (
    LanguageImportRequest,
    LanguageImportTarget,
)
from archives.codepot.src.contracts.language.runtime import LanguageImportStrategy, LanguageRuntime
from archives.codepot.src.languages.dart.syntax import (
    alias_module_path,
    import_line,
    package_module_path,
    relative_import_module_path,
)


def _module_for_target(
    target: LanguageImportTarget,
    runtime: LanguageRuntime,
    *,
    source_path: Path,
) -> tuple[LanguageImportKind, str]:
    """Create module URI from import strategy."""

    rules = runtime.imports

    if rules.strategy == LanguageImportStrategy.PACKAGE and rules.package:
        return (
            LanguageImportKind.PACKAGE,
            package_module_path(
                package=rules.package,
                target_path=target.target_path,
                root=rules.root,
                include_extension=rules.include_extension,
            ),
        )

    if rules.strategy == LanguageImportStrategy.ALIAS and rules.alias:
        return (
            LanguageImportKind.ALIAS,
            alias_module_path(
                alias_name=rules.alias,
                target_path=target.target_path,
                root=rules.root,
                include_extension=rules.include_extension,
            ),
        )

    return (
        LanguageImportKind.RELATIVE,
        relative_import_module_path(
            source_path=source_path,
            target_path=target.target_path,
            include_extension=rules.include_extension,
        ),
    )


def create_dart_imports(request: LanguageImportRequest) -> tuple[LanguageImport, ...]:
    """Create Dart file-level imports."""

    grouped: dict[tuple[LanguageImportKind, str], list[LanguageImportSymbol]] = {}

    for target in request.targets:
        if target.source_path == target.target_path:
            continue

        kind, module = _module_for_target(
            target,
            request.runtime,
            source_path=request.source_path,
        )

        key = (kind, module)
        grouped.setdefault(key, []).append(
            LanguageImportSymbol(
                name=target.symbol,
                alias=target.alias,
                is_type_only=False,
            )
        )

    imports: list[LanguageImport] = []

    for (kind, module), symbols in sorted(grouped.items(), key=lambda item: item[0][1]):
        visible_symbols = tuple(symbol.alias or symbol.name for symbol in symbols)
        rendered = import_line(module=module, symbols=visible_symbols)

        imports.append(
            LanguageImport(
                kind=kind,
                module=module,
                symbols=tuple(symbols),
                rendered=rendered,
                source_path=request.source_path,
                is_type_only=False,
            )
        )

    return tuple(imports)
