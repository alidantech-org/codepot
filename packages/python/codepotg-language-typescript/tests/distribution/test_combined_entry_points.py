from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Sequence

PYTHON_PACKAGES_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOTS = (
    PYTHON_PACKAGES_ROOT / "codepotg-v2",
    PYTHON_PACKAGES_ROOT / "codepotg-language-typescript",
    PYTHON_PACKAGES_ROOT / "codepotg-language-dart",
)

SMOKE_SCRIPT = textwrap.dedent(
    """
    from importlib.metadata import entry_points

    from codepotg.ports import (
        IdentifierRole,
        IdentifierValidationRequest,
        ModulePathRequest,
        OutputPathValidationRequest,
    )

    entries = {
        entry.name: entry
        for entry in entry_points(group="codepotg.language_adapters")
    }
    assert set(entries) == {"typescript", "dart"}, sorted(entries)

    typescript = entries["typescript"].load()()
    dart = entries["dart"].load()()

    assert typescript.plugin.id == "typescript"
    assert dart.plugin.id == "dart"
    assert {target.id for target in typescript.targets} == {
        "typescript",
        "typescript-jsx",
    }
    assert {target.id for target in dart.targets} == {"dart"}

    assert not typescript.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not typescript.validate_output_path(
        OutputPathValidationRequest("src/user.ts", "typescript")
    ).has_errors
    assert not typescript.validate_output_path(
        OutputPathValidationRequest("src/user.tsx", "typescript-jsx")
    ).has_errors
    assert (
        typescript.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact="src/user.ts",
            )
        ).specifier
        == "./user"
    )

    assert not dart.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not dart.validate_output_path(
        OutputPathValidationRequest("lib/src/user.dart", "dart")
    ).has_errors
    assert (
        dart.resolve_module_path(
            ModulePathRequest(
                "lib/src/service.dart",
                provider_artifact="lib/src/user.dart",
            )
        ).specifier
        == "./user.dart"
    )
    """
)


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        f"command failed: {command!r}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )


def _single_wheel(output: Path, prefix: str) -> Path:
    wheels = tuple(sorted(output.glob(f"{prefix}-*.whl")))
    assert len(wheels) == 1, wheels
    return wheels[0]


def _venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def test_dual_entry_points_from_fresh_built_wheels(tmp_path: Path) -> None:
    output = tmp_path / "dist"
    output.mkdir()

    for package_root in PACKAGE_ROOTS:
        _run(
            [
                sys.executable,
                "-m",
                "build",
                "--no-isolation",
                "--wheel",
                "--outdir",
                str(output),
                str(package_root),
            ],
            cwd=package_root,
        )

    wheels = (
        _single_wheel(output, "codepotg_core"),
        _single_wheel(output, "codepotg_language_typescript"),
        _single_wheel(output, "codepotg_language_dart"),
    )

    venv = tmp_path / "wheel-environment"
    _run([sys.executable, "-m", "venv", str(venv)], cwd=tmp_path)

    environment = os.environ.copy()
    environment["PYTHONNOUSERSITE"] = "1"
    environment.pop("PYTHONPATH", None)

    python = _venv_python(venv)
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--disable-pip-version-check",
            *(str(wheel) for wheel in wheels),
        ],
        cwd=tmp_path,
        env=environment,
    )
    _run(
        [str(python), "-c", SMOKE_SCRIPT],
        cwd=tmp_path,
        env=environment,
    )
