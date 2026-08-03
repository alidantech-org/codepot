from __future__ import annotations

import shutil
import subprocess
import tarfile
import zipfile
from importlib.metadata import distribution, entry_points
from pathlib import Path

import pytest
from dryv.versions import Version

import dryv_language_typescript

PACKAGE_ROOT = Path(__file__).parents[2]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[2]


@pytest.fixture(scope="module")
def built_distribution_artifacts(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path]:
    uv = shutil.which("uv")
    assert uv is not None, "distribution tests must run through the uv workspace"
    output = tmp_path_factory.mktemp("typescript-dist")
    completed = subprocess.run(
        [
            uv,
            "build",
            "--package",
            "dryv-language-typescript",
            "--out-dir",
            str(output),
            "--no-sources",
            "--no-build-isolation",
        ],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    wheels = tuple(sorted(output.glob("*.whl")))
    sdists = tuple(sorted(output.glob("*.tar.gz")))
    assert len(wheels) == 1, wheels
    assert len(sdists) == 1, sdists
    return wheels[0], sdists[0]


def test_distribution_metadata_typing_and_entry_point() -> None:
    package = distribution("dryv-language-typescript")
    assert package.version == "0.1.0a1"
    assert (Path(dryv_language_typescript.__file__).parent / "py.typed").is_file()
    entry = next(
        item
        for item in entry_points(group="dryv.language_adapters")
        if item.name == "typescript"
    )
    adapter = entry.load()()
    assert adapter.plugin.id == "typescript"
    assert adapter.plugin.version == Version.parse("0.1.0-alpha.1")


def test_built_wheel_contents(
    built_distribution_artifacts: tuple[Path, Path],
) -> None:
    wheel, _ = built_distribution_artifacts
    with zipfile.ZipFile(wheel) as archive:
        names = tuple(sorted(archive.namelist()))
    assert any(name == "dryv_language_typescript/py.typed" for name in names)
    assert any(name.endswith(".dist-info/entry_points.txt") for name in names)
    assert not any(name.startswith(("tests/", "benchmarks/")) for name in names)
    assert not any("dryv_language_dart" in name for name in names)
    assert not any("__pycache__" in name or ".pytest_cache" in name for name in names)


def test_built_sdist_excludes_generated_artifacts(
    built_distribution_artifacts: tuple[Path, Path],
) -> None:
    _, sdist = built_distribution_artifacts
    with tarfile.open(sdist, "r:gz") as archive:
        names = tuple(sorted(archive.getnames()))
    assert not any("/.venv/" in name or "/build/" in name for name in names)
    assert not any("__pycache__" in name or ".pytest_cache" in name for name in names)
