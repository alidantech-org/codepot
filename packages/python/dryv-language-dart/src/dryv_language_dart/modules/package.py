from __future__ import annotations

import re

from ..options import DartTargetOptions
from ..validation.paths import contained_parts

_PACKAGE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_PACKAGE_URI = re.compile(r"^package:([a-z][a-z0-9_]*)/(.+\.dart)$")


def package_uri(
    provider: str,
    project_root: str,
    options: DartTargetOptions,
) -> str:
    if options.package_name is None:
        raise ValueError("DART_MODULE_PATH_UNSUPPORTED: package_name option is required")
    if project_root != "lib":
        raise ValueError(
            "DART_MODULE_PATH_UNSUPPORTED: Dart package URIs require project_root='lib'"
        )
    provider_parts = contained_parts(provider)
    root_parts = contained_parts(project_root)
    if provider_parts[: len(root_parts)] != root_parts or len(provider_parts) == len(root_parts):
        raise ValueError(
            "DART_MODULE_PATH_ESCAPE: provider is outside the configured Dart library root"
        )
    subpath = "/".join(provider_parts[len(root_parts) :])
    if not subpath.endswith(".dart"):
        raise ValueError("DART_MODULE_PACKAGE_INVALID: package provider must be a .dart file")
    return f"package:{options.package_name}/{subpath}"


def validate_package_uri(value: str) -> str:
    match = _PACKAGE_URI.fullmatch(value)
    if match is None:
        raise ValueError("DART_MODULE_PACKAGE_INVALID: invalid package URI")
    path = match.group(2)
    if (
        "\\" in path
        or path.startswith("/")
        or "//" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
    ):
        raise ValueError("DART_MODULE_PACKAGE_INVALID: invalid package URI path")
    return value


def validate_package_name(value: str) -> str:
    if _PACKAGE_NAME.fullmatch(value) is None:
        raise ValueError("DART_MODULE_PACKAGE_INVALID: invalid Dart package name")
    return value
