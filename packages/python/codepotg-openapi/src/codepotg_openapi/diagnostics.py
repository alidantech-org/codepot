from __future__ import annotations

from dataclasses import dataclass, field

from codepotg.diagnostics import (
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    SourceSpan,
)


@dataclass(slots=True)
class DiagnosticBag:
    _items: list[Diagnostic] = field(default_factory=list)

    def add(
        self,
        code: str,
        severity: DiagnosticSeverity,
        message: str,
        *,
        span: SourceSpan | None = None,
        details: tuple[tuple[str, object], ...] = (),
        suggestion: str | None = None,
    ) -> None:
        self._items.append(
            Diagnostic(
                code=code,
                severity=severity,
                message=message,
                span=span,
                details=tuple(sorted(details)),
                suggestion=suggestion,
            )
        )

    def info(self, code: str, message: str, **kwargs: object) -> None:
        self.add(code, DiagnosticSeverity.INFO, message, **kwargs)

    def warning(self, code: str, message: str, **kwargs: object) -> None:
        self.add(code, DiagnosticSeverity.WARNING, message, **kwargs)

    def error(self, code: str, message: str, **kwargs: object) -> None:
        self.add(code, DiagnosticSeverity.ERROR, message, **kwargs)

    def fatal(self, code: str, message: str, **kwargs: object) -> None:
        self.add(code, DiagnosticSeverity.FATAL, message, **kwargs)

    @property
    def has_errors(self) -> bool:
        return any(item.is_error for item in self._items)

    def extend(self, diagnostics: Diagnostics) -> None:
        self._items.extend(diagnostics.items)

    def freeze(self) -> Diagnostics:
        return Diagnostics.from_iterable(self._items)
