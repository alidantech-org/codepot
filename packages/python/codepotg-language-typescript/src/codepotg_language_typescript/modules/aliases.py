from __future__ import annotations

from ..options import TypeScriptTargetOptions
from ..validation.paths import contained_parts
from .policies import apply_path_policies


def alias_specifier(
    provider: str,
    options: TypeScriptTargetOptions,
) -> str | None:
    provider_parts = contained_parts(provider)
    matches: list[tuple[int, str, tuple[str, ...]]] = []
    for binding in options.aliases:
        root_parts = tuple(binding.root.split("/"))
        if provider_parts[: len(root_parts)] == root_parts:
            matches.append(
                (len(root_parts), binding.alias, provider_parts[len(root_parts) :])
            )

    if not matches:
        return None

    matches.sort(key=lambda item: (-item[0], item[1]))
    if len(matches) > 1 and matches[0][0] == matches[1][0]:
        raise ValueError(
            "TS_MODULE_ALIAS_AMBIGUOUS: multiple aliases match the provider equally"
        )

    _, alias, remainder = matches[0]
    text = alias + (("/" + "/".join(remainder)) if remainder else "")
    return apply_path_policies(text, options) or alias
