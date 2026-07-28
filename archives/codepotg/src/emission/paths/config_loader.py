"""Load paths.yaml or paths.yml for template emission."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from archives.codepotg.src.contracts.path_yaml import PathYamlError, path_config_from_yaml
from archives.codepotg.src.contracts.paths import PathConfig, default_path_config

PATH_CONFIG_FILES = ("paths.yaml", "paths.yml")
SCHEMA_KEY = "$schema"


def resolve_path_config_file(template_root: Path) -> Path | None:
    """Resolve the single supported paths configuration file in a template pack."""
    found = [template_root / name for name in PATH_CONFIG_FILES if (template_root / name).is_file()]
    if len(found) > 1:
        names = ", ".join(path.name for path in found)
        raise PathYamlError(
            f"Template pack contains multiple paths configuration files: {names}. "
            "Keep only paths.yaml or paths.yml."
        )
    return found[0] if found else None


def load_path_config(template_root: Path, *, strict: bool = False) -> PathConfig:
    """Load paths.yaml/paths.yml from a template root if present.

    Generation uses compatibility mode by default. Author-facing inspection can
    enable strict mode to reject unknown keys before generation starts. The
    optional top-level ``$schema`` value is editor metadata and is retained on
    the typed contract without participating in generation planning.
    """
    path = resolve_path_config_file(template_root)
    if path is None:
        return default_path_config()

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return path_config_from_yaml(data, strict=strict)

    schema_uri = _optional_schema_uri(data.get(SCHEMA_KEY))
    authoring_data = dict(data)
    authoring_data.pop(SCHEMA_KEY, None)
    return replace(
        path_config_from_yaml(authoring_data, strict=strict),
        schema_uri=schema_uri,
    )


def _optional_schema_uri(raw: Any) -> str | None:
    if raw in (None, ""):
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise PathYamlError("paths.yaml $schema must be a non-empty string.")
    return raw.strip()
