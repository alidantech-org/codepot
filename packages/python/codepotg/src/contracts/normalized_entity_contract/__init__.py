"""Import-safe normalized entity contract.

The sibling compatibility module exposes a public rule property named ``field``.
Inside that dataclass body, the property name shadows ``dataclasses.field`` before
``raw_arguments`` is declared. Load the established implementation with that one
constructor qualified explicitly, preserving every public class and function.
"""

from __future__ import annotations

from pathlib import Path

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_entity_contract.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
_SHADOWED_DECLARATION = "raw_arguments: FrozenMap = field(default_factory=FrozenMap)"
_QUALIFIED_DECLARATION = (
    "raw_arguments: FrozenMap = "
    "__import__('dataclasses').field(default_factory=FrozenMap)"
)

if _SOURCE.count(_SHADOWED_DECLARATION) != 1:
    raise RuntimeError(
        "Normalized entity compatibility source no longer has the expected "
        "dataclass field declaration"
    )

_SOURCE = _SOURCE.replace(
    _SHADOWED_DECLARATION,
    _QUALIFIED_DECLARATION,
    1,
)
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102

del _QUALIFIED_DECLARATION
del _SHADOWED_DECLARATION
del _SOURCE
del _SOURCE_PATH
