from __future__ import annotations

import tarfile
import zipfile
from importlib.metadata import distribution, entry_points
from pathlib import Path

import codepotg_language_dart
import pytest

PACKAGE_ROOT = Path(__file__).parents[2]


def test_distribution_metadata_typing_and_entry_point() -> None:
    package = distribution("codepotg-language-dart")
    assert package.version == "0.1.0a1"
    assert (Path(codepotg_language_dart.__file__).parent / "py.typed").is_file()
    entry = next(
        item
        for item in entry_points(group="codepotg.language_adapters")
        if item.name == "dart"
    )
    adapter = entry.load()()
    assert adapter.plugin.id == "dart"


def test_built_wheel_contents_when_artifact_exists() -> None:
    wheels = tuple(sorted((PACKAGE_ROOT / "dist").glob("*.whl")))
    if not wheels:
        pytest.skip("build wheel before wheel-content verification")
    with zipfile.ZipFile(wheels[-1]) as archive:
        names = tuple(sorted(archive.namelist()))
    assert any(name == "codepotg_language_dart/py.typed" for name in names)
    assert any(name.endswith(".dist-info/entry_points.txt") for name in names)
    assert not any(name.startswith(("tests/", "benchmarks/")) for name in names)
    assert not any("codepotg_language_typescript" in name for name in names)
    assert not any("__pycache__" in name or ".pytest_cache" in name for name in names)


def test_built_sdist_excludes_generated_artifacts_when_present() -> None:
    sdists = tuple(sorted((PACKAGE_ROOT / "dist").glob("*.tar.gz")))
    if not sdists:
        pytest.skip("build sdist before sdist-content verification")
    with tarfile.open(sdists[-1], "r:gz") as archive:
        names = tuple(sorted(archive.getnames()))
    assert not any("/.venv/" in name or "/build/" in name for name in names)
    assert not any("__pycache__" in name or ".pytest_cache" in name for name in names)
