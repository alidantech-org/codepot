"""Dart export helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.exports import (
    LanguageExport,
    LanguageExportStrategy,
    LanguageExportSymbol,
)
from archives.codepot.src.contracts.language.interface import LanguageExportRequest
from archives.codepot.src.languages.dart.syntax import export_line, relative_import_module_path


def create_dart_exports(request: LanguageExportRequest) -> tuple[LanguageExport, ...]:
    """Create Dart file-level exports."""

    exports: list[LanguageExport] = []

    for target in request.targets:
        module = relative_import_module_path(
            source_path=request.source_path,
            target_path=target.target_path,
            include_extension=True,
        )

        symbol = LanguageExportSymbol(name=target.symbol, alias=target.alias)
        symbols = (symbol,)

        if request.strategy == LanguageExportStrategy.STAR:
            rendered = export_line(module=module)
        else:
            rendered_symbol = symbol.alias or symbol.name
            rendered = export_line(module=module, symbols=(rendered_symbol,))

        exports.append(
            LanguageExport(
                strategy=request.strategy,
                module=module,
                symbols=symbols,
                rendered=rendered,
                source_path=request.source_path,
                target_path=target.target_path,
            )
        )

    return tuple(exports)
