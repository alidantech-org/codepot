from pathlib import Path

import pytest

from dryv.config import PackManifest
from dryv.generation import PackDiscoveryError, PackFileKind, discover_pack_files
from dryv.runtime import RuntimePlugins


def _manifest() -> PackManifest:
    return PackManifest(
        api_version="dryv.dev/v1",
        id="example/static",
        version="1.0.0",
        description=None,
        include=("**/*",),
        exclude=("**/*.draft",),
        options=(),
        bindings=(),
        selections=(),
    )


def test_discovery_respects_manifest_and_pack_root_gitignore(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    templates = pack / "templates"
    templates.mkdir(parents=True)
    (pack / ".gitignore").write_text("templates/private/**\n", encoding="utf-8")
    (templates / "keep.txt").write_text("keep", encoding="utf-8")
    (templates / "skip.draft").write_text("draft", encoding="utf-8")
    (templates / "private").mkdir()
    (templates / "private" / "secret.txt").write_text("secret", encoding="utf-8")
    (templates / ".gitignore").write_text("ignored-control", encoding="utf-8")

    files = discover_pack_files(pack, _manifest(), RuntimePlugins())

    assert tuple(item.pack_path for item in files) == ("keep.txt",)
    assert files[0].kind is PackFileKind.STATIC


def test_discovery_denies_symlink_escape_when_supported(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    templates = pack / "templates"
    templates.mkdir(parents=True)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = templates / "link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")

    with pytest.raises(PackDiscoveryError, match="escapes"):
        discover_pack_files(pack, _manifest(), RuntimePlugins())
