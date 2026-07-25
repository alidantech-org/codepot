"""Compatibility loader for normalized frontend contracts.

Raw-only authored frontend metadata remains inspectable, but it must not be counted as
an unresolved reference. The sibling module defines the public dataclasses and builders;
this package narrows the aggregate count to the diagnostic category it names.
"""

from __future__ import annotations

from pathlib import Path

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_frontend_contract.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102


def _unresolved_count(self) -> int:
    return sum(
        diagnostic.category == DiagnosticCategory.UNRESOLVED
        for diagnostic in self.diagnostics
    )


NormalizedFrontendContract.unresolved_count = property(_unresolved_count)

del _SOURCE
del _SOURCE_PATH
