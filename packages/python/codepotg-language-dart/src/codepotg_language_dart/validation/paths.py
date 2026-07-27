from __future__ import annotations

import re
from pathlib import PurePosixPath

DEVICE_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)
_DRIVE = re.compile(r"^[A-Za-z]:")


def validate_lexical_path(path: str) -> tuple[str, ...]:
    errors: list[str] = []
    if not path:
        return ("empty",)
    if "\0" in path or any(
        ord(character) < 32 or ord(character) == 127 for character in path
    ):
        errors.append("control")
    if path.startswith("/") or _DRIVE.match(path) or path.startswith("//"):
        errors.append("absolute")
    if "\\" in path:
        errors.append("backslash")
    if any(character in path for character in '<>:"|?*'):
        errors.append("invalid_character")
    parts = path.split("/")
    if any(part == "" for part in parts):
        errors.append("empty_segment")
    if any(part == "." for part in parts):
        errors.append("dot_segment")
    if any(part == ".." for part in parts):
        errors.append("traversal")
    for part in parts:
        if part.endswith((".", " ")):
            errors.append("trailing_dot_space")
        if any(character.isspace() for character in part):
            errors.append("whitespace")
        if part.split(".", 1)[0].upper() in DEVICE_NAMES:
            errors.append("reserved_name")
    try:
        PurePosixPath(path)
    except ValueError:
        errors.append("invalid")
    return tuple(sorted(set(errors)))


def contained_parts(path: str) -> tuple[str, ...]:
    errors = validate_lexical_path(path)
    if errors:
        joined = ",".join(errors)
        raise ValueError(
            f"DART_MODULE_PATH_INVALID: invalid planned artifact path ({joined})"
        )
    return PurePosixPath(path).parts
