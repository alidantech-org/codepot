"""Python export helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.language.exports import (
    LanguageExport,
    LanguageExportStrategy,
    LanguageExportSymbol,
)
from archives.codepot.src.contracts.language.interface import LanguageExportRequest
from archives.codepot.src.languages.python.syntax import export_all_assignment


def create_python_exports(request: LanguageExportRequest) -> tuple[LanguageExport, ...]:
    """Create Python file-level exports.

    Python does not export from another module in the same way as TypeScript.
    For barrels, this creates an ``__all__`` assignment for emitted symbols.
    """

    symbols = tuple(
        LanguageExportSymbol(name=target.symbol, alias=target.alias)
        for target in request.targets
    )

    rendered_symbols = tuple(symbol.alias or symbol.name for symbol in symbols)
    rendered = export_all_assignment(rendered_symbols)

    return (
        LanguageExport(
            strategy=LanguageExportStrategy.NAMED,
            module="__all__",
            symbols=symbols,
            rendered=rendered,
            source_path=request.source_path,
        ),
    )
