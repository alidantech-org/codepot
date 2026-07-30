from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import jinja2
import markupsafe
import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CORE_ROOT = PACKAGE_ROOT.parent / "dryv"


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
    candidates = tuple(wheelhouse.glob("*.whl"))
    expected = "dryv_template_jinja" if project == PACKAGE_ROOT else "dryv_core"
    return next(path for path in candidates if path.name.startswith(expected))


@pytest.mark.distribution
def test_wheel_contents_are_isolated(tmp_path: Path) -> None:
    wheel = _build_wheel(PACKAGE_ROOT, tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        names = tuple(sorted(archive.namelist()))
    assert "dryv_template_jinja/py.typed" in names
    assert any(name.endswith("entry_points.txt") for name in names)
    forbidden = ("tests/", "benchmarks/", "dryv/domain/", ".github/")
    assert not any(any(part in name for part in forbidden) for name in names)


@pytest.mark.distribution
def test_isolated_wheels_discover_entry_point_and_render(tmp_path: Path) -> None:
    if not CORE_ROOT.exists():
        pytest.skip("sibling dryv package is unavailable")
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    core_wheel = _build_wheel(CORE_ROOT, wheelhouse)
    jinja_wheel = _build_wheel(PACKAGE_ROOT, wheelhouse)
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
    shutil.copytree(Path(jinja2.__file__).parent, isolated_site / "jinja2")
    shutil.copytree(Path(markupsafe.__file__).parent, isolated_site / "markupsafe")
    installed = subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            str(core_wheel),
            str(jinja_wheel),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    script = """
from importlib.metadata import entry_points
from dryv.api import CancellationToken
from dryv.ports import RenderRequest
entries = entry_points(group='dryv.template_engines')
entry = next(item for item in entries if item.name == 'jinja')
engine = entry.load()()
assert engine.plugin.id == 'jinja'
assert engine.suffixes == ('.j2', '.jinja', '.jinja2')
result = engine.render(RenderRequest('hello.txt.jinja', 'Hello {{ name }}', (('name', 'World'),)), CancellationToken())
assert result.content == 'Hello World'
assert not result.diagnostics.has_errors
partial = engine.render(RenderRequest('root.jinja', 'A{% include "p.jinja" %}C', (), (('p.jinja', 'B'),)), CancellationToken())
assert partial.content == 'ABC'
"""
    completed = subprocess.run(
        [str(python), "-I", "-c", script],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
