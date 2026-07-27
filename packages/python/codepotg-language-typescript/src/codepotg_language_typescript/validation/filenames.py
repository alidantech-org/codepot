from __future__ import annotations

from codepotg.diagnostics import Diagnostics
from codepotg.ports import OutputPathValidationRequest

from ..diagnostics import diagnostic
from ..targets import TARGETS, match_typescript_suffix
from .paths import validate_lexical_path

_DECLARATION_SUFFIXES = frozenset({".d.cts", ".d.mts", ".d.ts"})


def validate_output_path(request: OutputPathValidationRequest) -> Diagnostics:
    target = next(
        (item for item in TARGETS if item.id == request.target_id),
        None,
    )
    if target is None:
        return Diagnostics(
            (
                diagnostic(
                    "TS_TARGET_UNKNOWN",
                    "Unknown TypeScript target identifier",
                    target_id=request.target_id,
                ),
            )
        )

    found = []
    errors = validate_lexical_path(request.path)
    if errors:
        code = (
            "TS_FILE_RESERVED_NAME"
            if "reserved_name" in errors
            else "TS_FILE_PATH_INVALID"
        )
        found.append(
            diagnostic(
                code,
                "Invalid planned TypeScript output path",
                path=request.path,
                reasons=errors,
            )
        )

    suffix = match_typescript_suffix(request.path)
    if suffix is None:
        found.append(
            diagnostic(
                "TS_FILE_EXTENSION_INVALID",
                "Planned path does not use a recognized TypeScript suffix",
                path=request.path,
            )
        )
    elif suffix not in target.extensions:
        found.append(
            diagnostic(
                "TS_FILE_EXTENSION_INVALID",
                "Planned path suffix does not match the selected target",
                path=request.path,
                suffix=suffix,
                target_id=request.target_id,
            )
        )

    if suffix in _DECLARATION_SUFFIXES:
        name = request.path.rsplit("/", 1)[-1]
        if not name[: -len(suffix)]:
            found.append(
                diagnostic(
                    "TS_FILE_DECLARATION_INVALID",
                    "Declaration output requires a non-empty basename",
                    path=request.path,
                )
            )

    return Diagnostics.from_iterable(found)
