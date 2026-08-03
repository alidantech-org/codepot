from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Sequence
from pathlib import Path

PYTHON_PACKAGES_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = PYTHON_PACKAGES_ROOT.parents[1]
PACKAGE_NAMES = (
    ("dryv", "dryv-"),
    ("dryv-language-typescript", "dryv_language_typescript-"),
    ("dryv-language-dart", "dryv_language_dart-"),
)

SMOKE_SCRIPT = textwrap.dedent(
    """
    from importlib.metadata import entry_points

    from dryv.ports import (
        IdentifierRole,
        IdentifierValidationRequest,
        ModulePathRequest,
        OutputPathValidationRequest,
    )

    entries = {
        entry.name: entry
        for entry in entry_points(group="dryv.language_adapters")
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
        f"command failed: {command!r}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )


def _single_wheel(output: Path, prefix: str) -> Path:
    wheels = tuple(sorted(output.glob(f"{prefix}*.whl")))
    assert len(wheels) == 1, wheels
    return wheels[0]


def _venv_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def _uv_executable() -> str:
    executable = shutil.which("uv")
    assert executable is not None, "distribution tests must run through the uv workspace"
    return executable


def test_dual_entry_points_from_fresh_built_wheels(tmp_path: Path) -> None:
    uv = _uv_executable()
    output = tmp_path / "dist"
    output.mkdir()

    for package_name, _ in PACKAGE_NAMES:
        _run(
            [
                uv,
                "build",
                "--package",
                package_name,
                "--wheel",
                "--out-dir",
                str(output),
                "--no-sources",
                "--no-build-isolation",
            ],
            cwd=WORKSPACE_ROOT,
        )

    wheels = tuple(_single_wheel(output, prefix) for _, prefix in PACKAGE_NAMES)

    environment_path = tmp_path / "wheel-environment"
    _run(
        [uv, "venv", str(environment_path), "--python", sys.executable],
        cwd=WORKSPACE_ROOT,
    )

    environment = os.environ.copy()
    environment["PYTHONNOUSERSITE"] = "1"
    environment.pop("PYTHONPATH", None)

    python = _venv_python(environment_path)
    _run(
        [
            uv,
            "pip",
            "install",
            "--python",
            str(python),
            "--no-index",
            "--no-deps",
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
