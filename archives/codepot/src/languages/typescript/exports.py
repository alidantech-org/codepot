"""TypeScript export helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.exports import (
    LanguageExport,
    LanguageExportStrategy,
    LanguageExportSymbol,
)
from archives.codepot.src.contracts.language.interface import LanguageExportRequest
from archives.codepot.src.languages.typescript.syntax import (
    alias,
    export_named_line,
    export_star_line,
    relative_import_module_path,
)


def create_typescript_exports(
    request: LanguageExportRequest,
) -> tuple[LanguageExport, ...]:
    """Create TypeScript file-level exports."""

    exports: list[LanguageExport] = []

    for target in request.targets:
        module = relative_import_module_path(
            source_path=request.source_path,
            target_path=target.target_path,
            include_extension=False,
        )

        if request.strategy == LanguageExportStrategy.STAR:
            rendered = export_star_line(module=module)
            symbols: tuple[LanguageExportSymbol, ...] = ()
        else:
            symbol = LanguageExportSymbol(name=target.symbol, alias=target.alias)
            rendered_symbol = alias(symbol.name, symbol.alias)
            rendered = export_named_line(module=module, symbols=(rendered_symbol,))
            symbols = (symbol,)

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
