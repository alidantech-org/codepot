from __future__ import annotations

from pathlib import Path

import pytest

from emission.paths.config_loader import load_path_config


@pytest.mark.parametrize("pack", ["debug", "dart", "next", "typescript"])
def test_bundled_paths_configs_pass_strict_validation(pack: str) -> None:
    root = Path(__file__).parents[3] / "src" / "codepotg" / "templates" / pack

    config = load_path_config(root, strict=True)

    assert config.folders
