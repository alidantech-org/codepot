"""Load paths.yaml for template emission."""

from __future__ import annotations

from pathlib import Path

import yaml

from contracts.path_yaml import path_config_from_yaml
from contracts.paths import PathConfig, default_path_config

PATH_CONFIG_FILE = "paths.yaml"


def load_path_config(template_root: Path) -> PathConfig:
    """Load paths.yaml from a template root if present."""
    path = template_root / PATH_CONFIG_FILE

    if not path.exists():
        return default_path_config()

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return path_config_from_yaml(data if isinstance(data, dict) else {})
