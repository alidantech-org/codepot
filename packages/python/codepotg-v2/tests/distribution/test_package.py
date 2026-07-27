from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path
from zipfile import ZipFile

PACKAGE_ROOT = Path(__file__).parents[2]


def test_wheel_builds_contains_typed_package_tree_and_imports_in_isolation(
    tmp_path: Path,
) -> None:
    dist = tmp_path / "dist"
    _run(
        sys.executable,
        "-m",
        "build",
        "--wheel",
        "--no-isolation",
        "--outdir",
        str(dist),
        cwd=PACKAGE_ROOT,
    )
    wheels = tuple(dist.glob("codepotg_core-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]

    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
    expected = {
        "codepotg/__init__.py",
        "codepotg/api/__init__.py",
        "codepotg/diagnostics/__init__.py",
        "codepotg/domain/generation/__init__.py",
        "codepotg/domain/ir/__init__.py",
        "codepotg/generation/__init__.py",
        "codepotg/ir/__init__.py",
        "codepotg/plugins/__init__.py",
        "codepotg/ports/__init__.py",
        "codepotg/py.typed",
        "codepotg/testing/__init__.py",
        "codepotg/versions/__init__.py",
    }
    assert expected <= names

    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    scripts = "Scripts" if os.name == "nt" else "bin"
    python = environment / scripts / ("python.exe" if os.name == "nt" else "python")
    _run(
        str(python),
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--no-index",
        str(wheel),
    )
    completed = _run(
        str(python),
        "-c",
        (
            "import codepotg; "
            "from codepotg.generation import DEFAULT_SELECTOR_REGISTRY; "
            "from codepotg.ir import Contract; "
            "from codepotg.ports import SourceAdapter, TargetAdapter, TemplateEngine; "
            "print(codepotg.__version__)"
        ),
    )
    assert completed.stdout.strip() == "2.0.0-alpha.1"


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
