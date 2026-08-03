from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import jinja2
import markupsafe
import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PYTHON_PACKAGES_ROOT = PACKAGE_ROOT.parent
WORKSPACE_ROOT = PYTHON_PACKAGES_ROOT.parents[1]
CORE_ROOT = PYTHON_PACKAGES_ROOT / "dryv"
PACKAGE_NAMES = {
    CORE_ROOT: ("dryv", "dryv-"),
    PACKAGE_ROOT: ("dryv-template-jinja", "dryv_template_jinja-"),
}


def _build_wheel(project: Path, wheelhouse: Path) -> Path:
    uv = _uv_executable()
    package_name, prefix = PACKAGE_NAMES[project]
    completed = subprocess.run(
        [
            uv,
            "build",
            "--package",
            package_name,
            "--wheel",
            "--out-dir",
            str(wheelhouse),
            "--no-sources",
            "--no-build-isolation",
        ],
        cwd=WORKSPACE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    candidates = tuple(wheelhouse.glob("*.whl"))
    return next(path for path in candidates if path.name.startswith(prefix))


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
    uv = _uv_executable()
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    core_wheel = _build_wheel(CORE_ROOT, wheelhouse)
    jinja_wheel = _build_wheel(PACKAGE_ROOT, wheelhouse)
    environment = tmp_path / "venv"
    _run(uv, "venv", str(environment), "--python", sys.executable, cwd=WORKSPACE_ROOT)
    python = _venv_python(environment)
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
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "--force-reinstall",
            "--no-deps",
            "--no-index",
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


def _uv_executable() -> str:
    executable = shutil.which("uv")
    assert executable is not None, "distribution tests must run through the uv workspace"
    return executable


def _venv_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def _run(*arguments: str, cwd: Path | None = None) -> None:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
