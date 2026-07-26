from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path
from zipfile import ZipFile

PACKAGE_ROOT = Path(__file__).parents[1]


def test_wheel_builds_contains_typing_marker_and_imports_in_isolation(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)],
        cwd=PACKAGE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = tuple(dist.glob("codepotg_core-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]

    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert "codepotg/__init__.py" in names
    assert "codepotg/ir.py" in names
    assert "codepotg/ports.py" in names
    assert "codepotg/testing.py" in names
    assert "codepotg/py.typed" in names

    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    scripts = "Scripts" if os.name == "nt" else "bin"
    python = environment / scripts / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import codepotg; "
                "from codepotg.ir import Contract; "
                "from codepotg.ports import SourceAdapter, TargetAdapter, TemplateEngine; "
                "print(codepotg.__version__)"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "2.0.0-alpha.1"
