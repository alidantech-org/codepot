from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

PACKAGE_ROOT = Path(__file__).parents[2]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[2]


def test_wheel_builds_contains_typed_package_tree_and_imports_in_isolation(
    tmp_path: Path,
) -> None:
    uv = _uv_executable()
    dist = tmp_path / "dist"
    _run(
        uv,
        "build",
        "--package",
        "dryv",
        "--wheel",
        "--out-dir",
        str(dist),
        "--no-sources",
        "--no-build-isolation",
        cwd=WORKSPACE_ROOT,
    )
    wheels = tuple(dist.glob("dryv-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]

    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
    expected = {
        "dryv/__init__.py",
        "dryv/api/__init__.py",
        "dryv/diagnostics/__init__.py",
        "dryv/domain/generation/__init__.py",
        "dryv/domain/ir/__init__.py",
        "dryv/generation/__init__.py",
        "dryv/ir/__init__.py",
        "dryv/plugins/__init__.py",
        "dryv/ports/__init__.py",
        "dryv/py.typed",
        "dryv/testing/__init__.py",
        "dryv/versions/__init__.py",
    }
    assert expected <= names

    environment = tmp_path / "venv"
    _run(uv, "venv", str(environment), "--python", sys.executable, cwd=WORKSPACE_ROOT)
    python = _venv_python(environment)
    _run(
        uv,
        "pip",
        "install",
        "--python",
        str(python),
        "--no-deps",
        "--no-index",
        str(wheel),
    )
    completed = _run(
        str(python),
        "-c",
        (
            "import dryv; "
            "from dryv.generation import DEFAULT_SELECTOR_REGISTRY; "
            "from dryv.ir import Contract; "
            "from dryv.ports import SourceAdapter, TargetAdapter, TemplateEngine; "
            "print(dryv.__version__)"
        ),
    )
    assert completed.stdout.strip() == "2.0.0-alpha.1"


def _uv_executable() -> str:
    executable = shutil.which("uv")
    assert executable is not None, "distribution tests must run through the uv workspace"
    return executable


def _venv_python(environment: Path) -> Path:
    scripts = "Scripts" if os.name == "nt" else "bin"
    return environment / scripts / ("python.exe" if os.name == "nt" else "python")


def _run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        f"command failed ({completed.returncode}): {' '.join(arguments)}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
    return completed
