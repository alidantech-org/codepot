"""Tests for path folder recipe expansion."""

from __future__ import annotations

import pytest

from src.contracts.paths import PathConfig, PathFolder, PathSelectionMode, default_path_config
from src.emission.paths.selection import CONTEXT_FOLDER_PARTS, expand_folder_contexts


def test_expands_folder_each_mode():
    base_context = {
        "schemas": {
            "emit_models": [
                {"name": "User", "emit": {"resource_path": ("platform", "auth", "users")}},
                {"name": "Post", "emit": {"resource_path": ("content", "posts")}},
            ]
        }
    }

    path_config = PathConfig(
        folders=(
            PathFolder(
                name="model",
                select="schemas.emit_models",
                alias="model",
                parts=("docs", "resources", "[model.emit.resource_path]", "schemas", "models"),
                mode=PathSelectionMode.EACH,
            ),
        )
    )

    contexts = expand_folder_contexts(
        base_context=base_context,
        folder_name="model",
        path_config=path_config,
    )

    assert len(contexts) == 2
    assert contexts[0]["model"]["name"] == "User"
    assert contexts[0][CONTEXT_FOLDER_PARTS] == ("docs", "resources", "platform", "auth", "users", "schemas", "models")
    assert contexts[1][CONTEXT_FOLDER_PARTS] == ("docs", "resources", "content", "posts", "schemas", "models")


def test_folder_once_mode():
    base_context = {
        "api": {"version": "v1"},
    }

    path_config = PathConfig(
        folders=(
            PathFolder(
                name="version",
                select="api.version",
                alias="version",
                parts=("docs", "[version]"),
                mode=PathSelectionMode.ONCE,
            ),
        )
    )

    contexts = expand_folder_contexts(
        base_context=base_context,
        folder_name="version",
        path_config=path_config,
    )

    assert len(contexts) == 1
    assert contexts[0]["version"] == "v1"
    assert contexts[0][CONTEXT_FOLDER_PARTS] == ("docs", "v1")


def test_missing_folder_raises_error():
    base_context = {"schemas": {"emit_models": []}}
    path_config = default_path_config()

    with pytest.raises(KeyError, match="path folder not configured in paths.yaml: nonexistent"):
        expand_folder_contexts(
            base_context=base_context,
            folder_name="nonexistent",
            path_config=path_config,
        )


def test_folder_must_resolve_to_list_for_each_mode():
    base_context = {
        "schemas": {"emit_models": "not-a-list"},
    }

    path_config = PathConfig(
        folders=(
            PathFolder(
                name="model",
                select="schemas.emit_models",
                alias="model",
                parts=("docs",),
                mode=PathSelectionMode.EACH,
            ),
        )
    )

    with pytest.raises(TypeError, match="must resolve to a list/tuple"):
        expand_folder_contexts(
            base_context=base_context,
            folder_name="model",
            path_config=path_config,
        )
