from __future__ import annotations

from pathlib import Path

import pytest

from contracts.path_yaml import PathYamlError, path_config_from_yaml
from emission.paths.config_loader import load_path_config, resolve_path_config_file
from emission.templates.scanner import scan_templates


def test_load_path_config_supports_paths_yml(tmp_path: Path) -> None:
    (tmp_path / "paths.yml").write_text(
        """
folders:
  dto:
    select: schemas.emit_dtos
    as: dto
    parts: [src, dto]
""".strip(),
        encoding="utf-8",
    )

    config = load_path_config(tmp_path)

    assert resolve_path_config_file(tmp_path) == tmp_path / "paths.yml"
    assert config.folders[0].name == "dto"
    assert config.folders[0].select == "schemas.emit_dtos"
    assert "paths.yml" not in {
        descriptor.relative_path.as_posix() for descriptor in scan_templates(tmp_path)
    }


def test_load_path_config_rejects_both_yaml_extensions(tmp_path: Path) -> None:
    (tmp_path / "paths.yaml").write_text("folders: {}\n", encoding="utf-8")
    (tmp_path / "paths.yml").write_text("folders: {}\n", encoding="utf-8")

    with pytest.raises(PathYamlError, match="multiple paths configuration files"):
        load_path_config(tmp_path)


def test_path_config_rejects_unknown_top_level_key() -> None:
    with pytest.raises(PathYamlError, match="Unknown key.*include_hidden"):
        path_config_from_yaml({"include_hidden": True})


def test_path_config_rejects_unknown_folder_key() -> None:
    with pytest.raises(PathYamlError, match="Unknown key.*depends_on"):
        path_config_from_yaml(
            {
                "folders": {
                    "dto": {
                        "select": "schemas.emit_dtos",
                        "parts": ["src"],
                        "depends_on": ["enum"],
                    }
                }
            }
        )


def test_path_config_rejects_conflicting_alias_fields() -> None:
    with pytest.raises(PathYamlError, match="conflicting 'as' and 'alias'"):
        path_config_from_yaml(
            {
                "folders": {
                    "dto": {
                        "select": "schemas.emit_dtos",
                        "as": "dto",
                        "alias": "schema",
                        "parts": ["src"],
                    }
                }
            }
        )


def test_path_config_rejects_duplicate_effective_aliases() -> None:
    with pytest.raises(PathYamlError, match="same alias 'schema'"):
        path_config_from_yaml(
            {
                "folders": {
                    "dto": {
                        "select": "schemas.emit_dtos",
                        "as": "schema",
                        "parts": ["src", "dto"],
                    },
                    "model": {
                        "select": "schemas.emit_models",
                        "as": "schema",
                        "parts": ["src", "model"],
                    },
                }
            }
        )
