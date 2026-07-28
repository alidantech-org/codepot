from __future__ import annotations

from pathlib import PurePosixPath

from ..options import TypeScriptTargetOptions
from ..validation.paths import contained_parts
from .policies import apply_path_policies


def relative_specifier(
    current: str,
    provider: str,
    options: TypeScriptTargetOptions,
) -> str:
    current_parts = contained_parts(current)
    provider_parts = contained_parts(provider)
    base = current_parts[:-1]
    common = 0
    for left, right in zip(base, provider_parts, strict=False):
        if left != right:
            break
        common += 1

    parts = [".."] * (len(base) - common) + list(provider_parts[common:])
    text = "/".join(parts) or PurePosixPath(provider).name
    if not text.startswith("."):
        text = f"./{text}"

    return apply_path_policies(text, options) or "."
