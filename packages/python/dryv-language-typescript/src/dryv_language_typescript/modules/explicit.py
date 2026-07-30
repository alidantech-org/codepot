from __future__ import annotations

import re

from ..options import TypeScriptTargetOptions
from ..validation.paths import contained_parts
from .package import PACKAGE, validate_package

_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_FORBIDDEN = frozenset({"'", '"', ";", "\n", "\r", "\0"})


def validate_explicit(
    value: str,
    current: str,
    options: TypeScriptTargetOptions,
) -> str:
    if (
        not value
        or value.strip() != value
        or any(character in value for character in _FORBIDDEN)
        or "\\" in value
        or "//" in value
    ):
        raise ValueError("TS_MODULE_EXPLICIT_INVALID: explicit module contains forbidden syntax")
    words = set(value.lower().split())
    if words & {"import", "export"}:
        raise ValueError("TS_MODULE_EXPLICIT_INVALID: source fragments are not module specifiers")
    if _SCHEME.match(value):
        raise ValueError("TS_MODULE_PATH_UNSUPPORTED: URL schemes are not supported")
    if value.startswith(("./", "../")):
        _validate_relative(value, current)
        return value
    for binding in options.aliases:
        if value == binding.alias:
            return value
        if value.startswith(f"{binding.alias}/"):
            _validate_non_traversing_segments(value[len(binding.alias) + 1 :])
            return value
    if PACKAGE.fullmatch(value):
        return validate_package(value)
    raise ValueError("TS_MODULE_EXPLICIT_INVALID: unsupported explicit module specifier")


def _validate_relative(value: str, current: str) -> None:
    stack = list(contained_parts(current)[:-1])
    segments = value.split("/")
    for index, part in enumerate(segments):
        if part == "." and index == 0:
            continue
        if part == "..":
            if not stack:
                raise ValueError(
                    "TS_MODULE_PATH_ESCAPE: explicit relative module escapes the planned root"
                )
            stack.pop()
            continue
        if part in {"", "."}:
            raise ValueError("TS_MODULE_EXPLICIT_INVALID: invalid relative module segment")
        stack.append(part)


def _validate_non_traversing_segments(value: str) -> None:
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("TS_MODULE_ALIAS_INVALID: invalid alias module path")
