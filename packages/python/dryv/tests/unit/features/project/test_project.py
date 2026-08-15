from __future__ import annotations

import pytest

from dryv.config import ProjectConfig as LegacyProjectConfig
from dryv.features.project import (
    BuildMode,
    CacheMode,
    ProjectConfig,
    ProjectConfigurationError,
    decode_project,
)


def test_ir_resource_project_is_normalized_without_filesystem_access() -> None:
    project = decode_project({
        "apiVersion": "dryv.dev/v1",
        "name": "example",
        "sources": {"contract": {"resource": "resource://ir/main.jsonl"}},
        "packs": {},
        "resources": ["resource://project/templates", "resource://project/dryv.yaml"],
    })
    assert project.sources[0].kind == "ir"
    assert project.sources[0].resource == "resource://ir/main.jsonl"
    assert project.resources == ("resource://project/dryv.yaml", "resource://project/templates")
    assert project.cache_mode is CacheMode.USE
    assert project.build_mode is BuildMode.RENDER


def test_author_source_and_multiple_pack_instances_are_supported() -> None:
    project = decode_project({
        "apiVersion": "dryv.dev/v1",
        "name": "example",
        "sources": {
            "authored": {
                "author": "python",
                "resources": ["resource://author/app.py"],
                "options": {"strict": True},
            }
        },
        "packs": {
            "api": {
                "source": {"resource": "resource://packs/api"},
                "input": "authored",
                "output": "generated/api",
                "bindings": {"package": "example.api"},
            },
            "types": {
                "source": {"resource": "resource://packs/types"},
                "input": "authored",
                "output": "generated/types",
                "options": {"readonly": True},
            },
        },
        "bindings": {"workspace": "example"},
        "cache": "refresh",
        "build": "plan",
    })
    assert project.sources[0].kind == "author"
    assert tuple(item.name for item in project.packs) == ("api", "types")
    assert project.cache_mode is CacheMode.REFRESH
    assert project.build_mode is BuildMode.PLAN
    assert dict(project.bindings) == {"workspace": "example"}


def test_source_modes_are_mutually_exclusive() -> None:
    with pytest.raises(ProjectConfigurationError, match="exactly one"):
        decode_project({
            "apiVersion": "dryv.dev/v1",
            "name": "example",
            "sources": {"contract": {"resource": "resource://ir/main.json", "author": "python"}},
            "packs": {},
        })


def test_invalid_modes_and_unsafe_output_are_rejected() -> None:
    with pytest.raises(ProjectConfigurationError):
        decode_project({
            "apiVersion": "dryv.dev/v1",
            "name": "example",
            "sources": {"contract": {"resource": "resource://ir/main.json"}},
            "packs": {},
            "cache": "sometimes",
        })
    with pytest.raises(ProjectConfigurationError, match="POSIX-relative"):
        decode_project({
            "apiVersion": "dryv.dev/v1",
            "name": "example",
            "sources": {"contract": {"resource": "resource://ir/main.json"}},
            "packs": {"bad": {"source": {"resource": "resource://packs/bad"}, "input": "contract", "output": "/absolute"}},
        })


def test_legacy_config_namespace_reexports_project_feature_type() -> None:
    assert LegacyProjectConfig is ProjectConfig
