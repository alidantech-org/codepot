from __future__ import annotations

import re

from ..validation.paths import contained_parts
from .package import validate_package_uri

_DART_URI = re.compile(r"^dart:[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_FORBIDDEN = frozenset({"'", '"', ";", "\n", "\r", "\0"})


def validate_explicit(value: str, current: str) -> str:
    if (
        not value
        or value.strip() != value
        or any(character in value for character in _FORBIDDEN)
        or "\\" in value
    ):
        raise ValueError("DART_MODULE_EXPLICIT_INVALID: explicit URI contains forbidden syntax")

    if value.startswith("dart:"):
        if _DART_URI.fullmatch(value) is None:
            raise ValueError("DART_MODULE_EXPLICIT_INVALID: invalid dart: URI")
        return value

    if value.startswith("package:"):
        return validate_package_uri(value)

    if _SCHEME.match(value):
        raise ValueError(
            "DART_MODULE_PATH_UNSUPPORTED: network and file URI schemes are unsupported"
        )

    if value.startswith(("./", "../")):
        if not value.endswith(".dart"):
            raise ValueError("DART_MODULE_EXPLICIT_INVALID: relative Dart URI must end with .dart")
        _validate_relative(value, current)
        return value

    raise ValueError("DART_MODULE_EXPLICIT_INVALID: unsupported explicit Dart URI")


def _validate_relative(value: str, current: str) -> None:
    stack = list(contained_parts(current)[:-1])
    for index, part in enumerate(value.split("/")):
        if part == "." and index == 0:
            continue
        if part == "..":
            if not stack:
                raise ValueError(
                    "DART_MODULE_PATH_ESCAPE: explicit relative URI escapes the planned root"
                )
            stack.pop()
            continue
        if part in {"", "."}:
            raise ValueError("DART_MODULE_EXPLICIT_INVALID: invalid relative URI segment")
        stack.append(part)
