"""Compatibility loader for the legacy normalized domain view.

The newer specialized normalized roots classify unresolved plain registry names
as internal ``missing`` references. The older broad ``domains`` root historically
classified those plain names as ``external``. Keep that compatibility contract
local to this root while URI/file and JSON-pointer behavior remains unchanged.
"""

from __future__ import annotations

from pathlib import Path

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_domains.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
_IMPORT = (
    "from contracts.normalized_builders import build_reference, build_schema_use"
)
_REPLACEMENT = """from contracts.normalized_builders import (
    build_reference as _strict_build_reference,
    build_schema_use,
)


def build_reference(ref, *, kind, owner, source_path, targets):
    value = _strict_build_reference(
        ref,
        kind=kind,
        owner=owner,
        source_path=source_path,
        targets=targets,
    )
    normalized = __import__(
        'contracts.normalized',
        fromlist=['ResolutionState'],
    )
    if value.state == normalized.ResolutionState.MISSING and not ref.startswith('#/'):
        return __import__('dataclasses').replace(
            value,
            state=normalized.ResolutionState.EXTERNAL,
            diagnostics=(),
        )
    return value
"""

if _SOURCE.count(_IMPORT) != 1:
    raise RuntimeError(
        "Normalized domains compatibility source no longer has the expected "
        "builder import"
    )

_SOURCE = _SOURCE.replace(_IMPORT, _REPLACEMENT, 1)
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102

del _IMPORT
del _REPLACEMENT
del _SOURCE
del _SOURCE_PATH
