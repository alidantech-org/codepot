from __future__ import annotations

from dryv.diagnostics import Diagnostics
from dryv.ports import OutputPathValidationRequest

from ..diagnostics import diagnostic
from .paths import validate_lexical_path


def validate_output_path(request: OutputPathValidationRequest) -> Diagnostics:
    if request.target_id != "dart":
        return Diagnostics(
            (
                diagnostic(
                    "DART_TARGET_UNKNOWN",
                    "Unknown Dart target identifier",
                    target_id=request.target_id,
                ),
            )
        )

    found = []
    errors = validate_lexical_path(request.path)
    if errors:
        code = "DART_FILE_RESERVED_NAME" if "reserved_name" in errors else "DART_FILE_PATH_INVALID"
        found.append(
            diagnostic(
                code,
                "Invalid planned Dart output path",
                path=request.path,
                reasons=errors,
            )
        )

    if not request.path.endswith(".dart"):
        found.append(
            diagnostic(
                "DART_FILE_EXTENSION_INVALID",
                "Planned path must end with .dart",
                path=request.path,
            )
        )

    return Diagnostics.from_iterable(found)
