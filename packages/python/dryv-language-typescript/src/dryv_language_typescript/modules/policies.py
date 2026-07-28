from __future__ import annotations

from ..options import (
    IndexResolutionPolicy,
    TypeScriptExtensionPolicy,
    TypeScriptTargetOptions,
)
from ..targets import match_typescript_suffix


def apply_path_policies(value: str, options: TypeScriptTargetOptions) -> str:
    suffix = match_typescript_suffix(value)
    without_suffix = value[: -len(suffix)] if suffix else value

    if (
        options.index_policy is IndexResolutionPolicy.OMIT_INDEX
        and without_suffix.rsplit("/", 1)[-1] == "index"
    ):
        return without_suffix.rpartition("/")[0]

    if suffix is not None and options.extension_policy is TypeScriptExtensionPolicy.OMIT_TYPESCRIPT:
        return without_suffix

    return value
