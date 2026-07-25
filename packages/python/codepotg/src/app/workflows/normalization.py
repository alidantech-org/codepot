"""Conservative normalized-root demand detection for template packs."""

from __future__ import annotations

import os
from pathlib import Path

ALL_NORMALIZED_ROOTS = frozenset(
    {
        "normalized",
        "normalized_domains",
        "normalized_schemas",
        "normalized_codegen",
        "normalized_entities",
        "normalized_frontends",
    }
)

_TOKEN_ROOTS = {
    "schema_contract": "normalized_schemas",
    "codegen_contract": "normalized_codegen",
    "entity_contract": "normalized_entities",
    "frontend_contract": "normalized_frontends",
    "normalized_domains": "normalized_domains",
    "normalized_schemas": "normalized_schemas",
    "normalized_codegen": "normalized_codegen",
    "normalized_entities": "normalized_entities",
    "normalized_frontends": "normalized_frontends",
}
_TEMPLATE_SUFFIXES = frozenset(
    {
        ".j2",
        ".jinja",
        ".jinja2",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".json",
    }
)


def required_normalized_roots(template_root: Path) -> frozenset[str]:
    """Return roots explicitly referenced by a pack, conservatively falling back."""
    override = os.getenv("CODEPOTG_NORMALIZED_ROOTS", "").strip()
    if override:
        lowered = override.lower()
        if lowered in {"all", "*", "full"}:
            return ALL_NORMALIZED_ROOTS
        if lowered in {"none", "off", "0"}:
            return frozenset()
        requested = {
            value.strip()
            for value in override.split(",")
            if value.strip()
        }
        unknown = requested - ALL_NORMALIZED_ROOTS
        if unknown:
            raise ValueError(
                "Unknown CODEPOTG_NORMALIZED_ROOTS values: "
                + ", ".join(sorted(unknown))
            )
        return _dependency_closure(requested)

    requested: set[str] = set()
    uncertain = False
    for path in _template_files(template_root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        lowered = text.lower()
        for token, root in _TOKEN_ROOTS.items():
            if token in lowered:
                requested.add(root)
        if "api.meta" in lowered or "api['meta']" in lowered or 'api["meta"]' in lowered:
            uncertain = True
        if "normalized" in lowered and not any(
            token in lowered for token in _TOKEN_ROOTS
        ):
            requested.add("normalized")

    if uncertain:
        return ALL_NORMALIZED_ROOTS
    return _dependency_closure(requested)


def _dependency_closure(values: set[str]) -> frozenset[str]:
    requested = set(values)
    if "normalized_codegen" in requested:
        requested.update({"normalized_domains", "normalized_entities"})
    return frozenset(requested)


def _template_files(root: Path):
    if not root.is_dir():
        return ()
    return (
        path
        for path in root.rglob("*")
        if path.is_file()
        and (
            path.suffix.lower() in _TEMPLATE_SUFFIXES
            or path.name in {"paths.yaml", "paths.yml"}
        )
    )
