"""JSON Schema and loader parity for CodepotG authoring files."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from codepot_file.loader import load_codepotg_config
from codepotg.schemas import (
    CODEPOTG_SCHEMA_ID,
    PATHS_SCHEMA_ID,
    load_schema,
    schema_path,
)
from contracts.path_yaml import PathYamlError
from emission.paths.config_loader import load_path_config


def test_bundled_authoring_schemas_are_valid_draft_2020_12() -> None:
    for name in ("codepotg", "paths"):
        path = schema_path(name)
        assert path.is_file()
        Draft202012Validator.check_schema(load_schema(name))


def test_codepotg_schema_matches_loader_contract(tmp_path: Path) -> None:
    document = {
        "$schema": CODEPOTG_SCHEMA_ID,
        "allow": True,
        "defaults": {
            "templateDir": "templates",
            "env": {"GENERATION_MODE": "strict", "WORKERS": 4},
        },
        "tasks": {
            "client": {
                "input": "openapi.json",
                "language": "python",
                "output": "generated",
                "clean": ["generated"],
                "before": ["python prepare.py"],
                "after": [
                    {
                        "name": "format",
                        "run": "ruff format generated",
                        "optional": True,
                    }
                ],
            }
        },
    }
    Draft202012Validator(load_schema("codepotg")).validate(document)

    config = tmp_path / "Codepotg.yaml"
    config.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    loaded = load_codepotg_config(config)

    assert loaded.schema_uri == CODEPOTG_SCHEMA_ID
    assert loaded.allow is True
    assert loaded.tasks[0].language == "python"
    assert loaded.tasks[0].template_dir == (tmp_path / "templates").resolve()


def test_paths_schema_matches_strict_loader_contract(tmp_path: Path) -> None:
    document = {
        "$schema": PATHS_SCHEMA_ID,
        "template_extension": ".j2",
        "strip_template_extension": True,
        "allow_raw_files": False,
        "imports": {"strategy": "relative"},
        "write_policy": {
            "default_mode": "managed",
            "managed_roots": ["generated"],
            "immutable_roots": ["generated/barrels"],
            "protected_roots": ["generated"],
            "clean_roots": ["generated"],
        },
        "selections": {
            "models": {
                "select": "schemas.emit_models",
                "as": "model",
                "scope": "each",
            }
        },
        "emissions": {
            "model-files": {
                "selection": "models",
                "template": "model.py.j2",
                "output": ["generated", "models", "[model.emit.file_name]"],
                "provides": ["models"],
            }
        },
        "barrels": {
            "model-barrel": {
                "template": "barrel.py.j2",
                "output": ["generated", "barrels", "models.py"],
                "exports": ["model-files"],
                "lifecycle": "immutable",
            }
        },
    }
    Draft202012Validator(load_schema("paths")).validate(document)

    template_root = tmp_path / "templates"
    template_root.mkdir()
    (template_root / "paths.yaml").write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding="utf-8",
    )
    loaded = load_path_config(template_root, strict=True)

    assert loaded.schema_uri == PATHS_SCHEMA_ID
    assert loaded.uses_graph is True
    assert loaded.output_node_names() == ("model-barrel", "model-files")


def test_paths_schema_reference_does_not_weaken_strict_unknown_key_validation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    (template_root / "paths.yaml").write_text(
        yaml.safe_dump(
            {
                "$schema": PATHS_SCHEMA_ID,
                "unexpected": True,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(PathYamlError, match="unexpected"):
        load_path_config(template_root, strict=True)


def test_schema_reference_must_be_a_non_empty_string(tmp_path: Path) -> None:
    config = tmp_path / "Codepotg.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "$schema": 42,
                "allow": True,
                "tasks": {
                    "client": {
                        "input": "openapi.json",
                        "language": "python",
                        "output": "generated",
                    }
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(Exception, match=r"\$schema"):
        load_codepotg_config(config)
