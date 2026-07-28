from pathlib import Path

import pytest

from dryv.config import PackManifest, SelectionConfig
from dryv.generation.manifest_validation import (
    require_pack_contained,
    validate_pack_compatibility,
    validate_selection_graph,
)


def _manifest(*, requires=(), selections=()) -> PackManifest:
    return PackManifest(
        api_version="dryv.dev/v1",
        id="example/pack",
        version="1.0.0",
        description=None,
        include=("**/*",),
        exclude=(),
        options=(),
        bindings=(),
        selections=selections,
        requires=requires,
    )


def test_pack_compatibility_accepts_current_api_ranges() -> None:
    validate_pack_compatibility(
        _manifest(
            requires=(
                ("dryv", ">=2.0.0a1,<3.0"),
                ("ir", ">=2.0,<3.0"),
            )
        )
    )


def test_pack_compatibility_and_selection_cycles_fail_before_planning() -> None:
    with pytest.raises(ValueError, match="PACK_REQUIREMENT_UNSATISFIED"):
        validate_pack_compatibility(_manifest(requires=(("dryv", ">=3.0"),)))

    with pytest.raises(ValueError, match="PLAN_SELECTION_CYCLE"):
        validate_selection_graph(
            _manifest(
                selections=(
                    SelectionConfig(key="a", exports=("b",)),
                    SelectionConfig(key="b", exports=("a",)),
                )
            )
        )


def test_local_pack_must_remain_inside_project_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    pack = project / "packs" / "local"
    pack.mkdir(parents=True)
    assert require_pack_contained(pack, project) == pack.resolve()

    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError, match="PACK_SOURCE_ESCAPE"):
        require_pack_contained(outside, project)
