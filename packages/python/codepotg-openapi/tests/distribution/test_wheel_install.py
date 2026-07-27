from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CORE_ROOT = PACKAGE_ROOT.parent / "codepotg-v2"


def _build_wheel(project: Path, wheelhouse: Path) -> Path:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheelhouse),
            str(project),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    prefix = "codepotg_openapi" if project == PACKAGE_ROOT else "codepotg_core"
    return next(path for path in wheelhouse.glob("*.whl") if path.name.startswith(prefix))


def test_wheel_contains_entry_point_and_no_private_core_or_tests(tmp_path: Path) -> None:
    wheel = _build_wheel(PACKAGE_ROOT, tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        names = tuple(sorted(archive.namelist()))
    assert "codepotg_openapi/adapter.py" in names
    assert "codepotg_openapi/py.typed" in names
    assert any(name.endswith("entry_points.txt") for name in names)
    forbidden = ("tests/", "benchmarks/", "codepotg/domain/", ".github/")
    assert not any(any(part in name for part in forbidden) for name in names)


def test_isolated_wheels_load_entry_point_and_normalize(tmp_path: Path) -> None:
    assert CORE_ROOT.exists(), "sibling codepotg-v2 package is required"
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    core_wheel = _build_wheel(CORE_ROOT, wheelhouse)
    adapter_wheel = _build_wheel(PACKAGE_ROOT, wheelhouse)

    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    site_result = subprocess.run(
        [str(python), "-c", "import site; print(site.getsitepackages()[0])"],
        check=True,
        capture_output=True,
        text=True,
    )
    isolated_site = Path(site_result.stdout.strip())
    shutil.copytree(Path(yaml.__file__).parent, isolated_site / "yaml")

    installed = subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            str(core_wheel),
            str(adapter_wheel),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr

    script = r'''
import json
from importlib.metadata import entry_points
from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapter, SourceAdapterRequest
entries = entry_points(group="codepotg.source_adapters")
entry = next(item for item in entries if item.name == "openapi")
adapter = entry.load()()
assert isinstance(adapter, SourceAdapter)
result = adapter.normalize(
    SourceAdapterRequest(
        source_id="isolated",
        content=json.dumps({
            "openapi": "3.1.0",
            "info": {"title": "Isolated", "version": "1"},
            "paths": {},
        }),
    ),
    CancellationToken(),
)
assert result.contract is not None
assert result.contract.name.value == "Isolated"
assert result.digest and len(result.digest) == 64
assert not result.diagnostics.has_errors
'''
    completed = subprocess.run(
        [str(python), "-I", "-c", script],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
