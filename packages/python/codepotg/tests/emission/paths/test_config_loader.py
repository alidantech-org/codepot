from __future__ import annotations

from pathlib import Path

import pytest

from contracts.path_yaml import PathYamlError, path_config_from_yaml
from contracts.paths import PathSelectionScope
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


def test_path_config_strict_mode_rejects_unknown_top_level_key() -> None:
    with pytest.raises(PathYamlError, match="Unknown key.*include_hidden"):
        path_config_from_yaml({"include_hidden": True}, strict=True)


def test_path_config_compatibility_mode_preserves_unknown_top_level_key() -> None:
    config = path_config_from_yaml({"include_hidden": True})

    assert config.folders == ()


def test_path_config_strict_mode_rejects_unknown_folder_key() -> None:
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
            },
            strict=True,
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


def test_path_config_allows_alias_reuse_across_folder_recipes() -> None:
    config = path_config_from_yaml(
        {
            "folders": {
                "route_group": {
                    "select": "features",
                    "as": "resource",
                    "parts": ["routes"],
                },
                "feature": {
                    "select": "features",
                    "as": "resource",
                    "parts": ["features"],
                },
            }
        },
        strict=True,
    )

    assert [folder.alias for folder in config.folders] == ["resource", "resource"]


def test_path_config_parses_named_selection_emission_and_barrel_graph() -> None:
    config = path_config_from_yaml(
        {
            "selections": {
                "dtos": {
                    "select": "schemas.emit_dtos",
                    "as": "dto",
                    "scope": "each",
                },
                "enums": {
                    "select": "schemas.emit_enums",
                    "as": "enum",
                    "scope": "each",
                },
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "templates/dto.type.ts.j2",
                    "output": ["models", ["dto.name.path.o"], "type.ts"],
                    "imports": {"enums": "enum-types"},
                    "provides": ["dtos"],
                },
                "enum-types": {
                    "selection": "enums",
                    "template": "templates/enum.ts.j2",
                    "output": ["models", ["enum.name.path.o"], "enum.ts"],
                    "provides": ["enums"],
                },
            },
            "barrels": {
                "models": {
                    "template": "templates/models.index.ts.j2",
                    "output": ["models", "index.ts"],
                    "exports": ["dto-types", "enum-types"],
                    "scope": "all",
                }
            },
        },
        strict=True,
    )

    assert config.uses_graph
    assert config.selections[0].scope == PathSelectionScope.EACH
    assert config.emissions[0].provider_by_purpose()["enums"].source == "enum-types"
    assert config.emissions[0].output == ("models", "[dto.name.path.o]", "type.ts")
    assert config.barrels[0].exports == ("dto-types", "enum-types")
    assert config.output_node_names() == ("dto-types", "enum-types", "models")


def test_path_config_allows_legacy_folders_and_graph_to_coexist() -> None:
    config = path_config_from_yaml(
        {
            "folders": {
                "legacy": {
                    "select": "schemas.emit_dtos",
                    "as": "dto",
                    "parts": ["legacy"],
                }
            },
            "selections": {
                "dtos": {"select": "schemas.emit_dtos", "as": "dto"}
            },
            "emissions": {
                "dto-types": {
                    "selection": "dtos",
                    "template": "dto.ts.j2",
                    "output": ["models", ["dto.name.path.o"], "dto.ts"],
                }
            },
        },
        strict=True,
    )

    assert config.folders[0].name == "legacy"
    assert config.emissions[0].name == "dto-types"


def test_path_config_rejects_unknown_selection_provider_and_export() -> None:
    with pytest.raises(PathYamlError, match="unknown selection 'missing'"):
        path_config_from_yaml(
            {
                "emissions": {
                    "dto-types": {
                        "selection": "missing",
                        "template": "dto.ts.j2",
                        "output": ["dto.ts"],
                    }
                }
            }
        )

    with pytest.raises(PathYamlError, match="unknown provider 'missing-provider'"):
        path_config_from_yaml(
            {
                "selections": {"dtos": {"select": "schemas.emit_dtos"}},
                "emissions": {
                    "dto-types": {
                        "selection": "dtos",
                        "template": "dto.ts.j2",
                        "output": ["dto.ts"],
                        "imports": {"enums": "missing-provider"},
                    }
                },
            }
        )

    with pytest.raises(PathYamlError, match="exports unknown output node 'missing'"):
        path_config_from_yaml(
            {
                "barrels": {
                    "models": {
                        "template": "index.ts.j2",
                        "output": ["index.ts"],
                        "exports": ["missing"],
                    }
                }
            }
        )


def test_path_config_rejects_selection_alias_ambiguity() -> None:
    with pytest.raises(PathYamlError, match="use the same alias 'item'"):
        path_config_from_yaml(
            {
                "selections": {
                    "dtos": {"select": "schemas.emit_dtos", "as": "item"},
                    "enums": {"select": "schemas.emit_enums", "as": "item"},
                }
            }
        )


def test_path_config_rejects_output_dependency_cycles() -> None:
    with pytest.raises(PathYamlError, match=r"cycle: first -> second -> first"):
        path_config_from_yaml(
            {
                "selections": {"dtos": {"select": "schemas.emit_dtos"}},
                "emissions": {
                    "first": {
                        "selection": "dtos",
                        "template": "first.ts.j2",
                        "output": ["first.ts"],
                        "imports": {"dtos": "second"},
                    },
                    "second": {
                        "selection": "dtos",
                        "template": "second.ts.j2",
                        "output": ["second.ts"],
                        "imports": {"dtos": "first"},
                    },
                },
            }
        )


def test_path_config_rejects_unsafe_template_and_each_barrel() -> None:
    with pytest.raises(PathYamlError, match="safe relative POSIX path"):
        path_config_from_yaml(
            {
                "selections": {"dtos": {"select": "schemas.emit_dtos"}},
                "emissions": {
                    "dto-types": {
                        "selection": "dtos",
                        "template": "../dto.ts.j2",
                        "output": ["dto.ts"],
                    }
                },
            }
        )

    with pytest.raises(PathYamlError, match="must be 'all' or 'resource'"):
        path_config_from_yaml(
            {
                "barrels": {
                    "models": {
                        "template": "index.ts.j2",
                        "output": ["index.ts"],
                        "exports": ["models-direct"],
                        "scope": "each",
                    }
                },
                "selections": {"models": {"select": "schemas.emit_models"}},
                "emissions": {
                    "models-direct": {
                        "selection": "models",
                        "template": "model.ts.j2",
                        "output": ["model.ts"],
                    }
                },
            }
        )
