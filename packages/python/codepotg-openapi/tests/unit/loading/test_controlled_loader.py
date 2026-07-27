from __future__ import annotations

import json
from pathlib import Path

import pytest
from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest

from codepotg_openapi.loading.controlled_loader import ControlledSourceLoader, SourceLoadError
from codepotg_openapi.loading.policy import SourcePolicy
from codepotg_openapi.options import OpenApiOptions


def test_memory_root_is_loaded_without_filesystem_authority() -> None:
    loader = ControlledSourceLoader(source_policy=SourcePolicy(), reference_loader=None)
    source = loader.load_root(
        SourceAdapterRequest(source_id="memory", content="{}"),
        OpenApiOptions(),
        CancellationToken(),
    )
    assert source.canonical_id == "memory:memory"
    assert source.path is None


def test_relative_root_path_is_rejected() -> None:
    loader = ControlledSourceLoader(source_policy=SourcePolicy(), reference_loader=None)
    with pytest.raises(SourceLoadError) as error:
        loader.load_root(
            SourceAdapterRequest(source_id="relative", location="openapi.yaml"),
            OpenApiOptions(),
            CancellationToken(),
        )
    assert error.value.code == "OA_SOURCE_RELATIVE_PATH"


def test_absolute_root_file_is_contained(tmp_path: Path) -> None:
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps({"openapi": "3.1.0"}))
    loader = ControlledSourceLoader(source_policy=SourcePolicy(), reference_loader=None)
    source = loader.load_root(
        SourceAdapterRequest(source_id="local", location=str(path.resolve())),
        OpenApiOptions(),
        CancellationToken(),
    )
    assert source.path == path.resolve()
    assert source.authorized_root == tmp_path.resolve()
