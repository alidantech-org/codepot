from __future__ import annotations

import re

from ..options import TypeScriptTargetOptions
from ..validation.paths import contained_parts
from .policies import apply_path_policies

PACKAGE = re.compile(r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*(?:/[A-Za-z0-9._-]+)*$")


def validate_package(value: str) -> str:
    if PACKAGE.fullmatch(value) is None or any(
        part in {"", ".", ".."} for part in value.split("/")
    ):
        raise ValueError("TS_MODULE_PACKAGE_INVALID: invalid npm-style package specifier")
    return value


def provider_package_specifier(
    provider: str,
    project_root: str,
    options: TypeScriptTargetOptions,
) -> str:
    if options.package_name is None:
        raise ValueError("TS_MODULE_PATH_UNSUPPORTED: package_name option is required")

    provider_parts = contained_parts(provider)
    root_parts = contained_parts(project_root)
    if provider_parts[: len(root_parts)] != root_parts or len(provider_parts) == len(root_parts):
        raise ValueError("TS_MODULE_PATH_ESCAPE: provider is outside the configured project root")

    subpath = "/".join(provider_parts[len(root_parts) :])
    subpath = apply_path_policies(subpath, options)
    if not subpath:
        return options.package_name
    return f"{options.package_name}/{subpath}"
