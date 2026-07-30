"""Native syntax and build validation for generated portable-language packages."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app import GeneratorApp

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "portable_languages"


def _generate(tmp_path: Path, language: str) -> Path:
    workspace = Path(shutil.copytree(FIXTURE_ROOT, tmp_path / "portable_languages"))
    config = workspace / language / "Codepotg.yml"
    result = GeneratorApp().generate(config_path=config, task_name="fixture")
    task = result.tasks[0]
    assert task.refused == []
    assert len(task.written) == len(task.planned)
    return workspace / language / ".generated-review" / "package"


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"command failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def _skip_for_missing_offline_dependency(
    result: subprocess.CompletedProcess[str],
    *,
    markers: tuple[str, ...],
) -> None:
    if result.returncode == 0:
        return
    output = f"{result.stdout}\n{result.stderr}".lower()
    if any(marker.lower() in output for marker in markers):
        pytest.skip("native dependencies are not available in the local offline cache")


def test_generated_python_package_byte_compiles(tmp_path: Path) -> None:
    package = _generate(tmp_path, "python")
    result = _run(
        [sys.executable, "-m", "compileall", "-q", "src"],
        cwd=package,
    )
    _assert_success(result)


def test_generated_java_package_compiles_when_javac_is_available(tmp_path: Path) -> None:
    javac = shutil.which("javac")
    if javac is None:
        pytest.skip("javac is not installed")

    package = _generate(tmp_path, "java")
    sources = sorted(
        str(path) for path in (package / "src" / "main" / "java").rglob("*.java")
    )
    assert sources
    classes = package / "target" / "fixture-classes"
    classes.mkdir(parents=True, exist_ok=True)
    result = _run([javac, "-d", str(classes), *sources], cwd=package)
    _assert_success(result)


def test_generated_csharp_package_builds_when_dotnet_is_available(tmp_path: Path) -> None:
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        pytest.skip("dotnet is not installed")

    package = _generate(tmp_path, "csharp")
    result = _run(
        [dotnet, "build", "GeneratedClient.csproj", "--nologo"],
        cwd=package,
    )
    _assert_success(result)


def test_generated_go_sources_are_gofmt_clean_when_available(tmp_path: Path) -> None:
    gofmt = shutil.which("gofmt")
    if gofmt is None:
        pytest.skip("gofmt is not installed")

    package = _generate(tmp_path, "go")
    sources = sorted(str(path) for path in package.rglob("*.go"))
    assert sources
    result = _run([gofmt, "-d", *sources], cwd=package)
    _assert_success(result)
    assert result.stdout == "", result.stdout


def test_generated_go_package_compiles_offline_when_dependencies_are_cached(
    tmp_path: Path,
) -> None:
    go = shutil.which("go")
    if go is None:
        pytest.skip("go is not installed")

    package = _generate(tmp_path, "go")
    env = os.environ.copy()
    env.update({"GOPROXY": "off", "GOSUMDB": "off"})
    result = _run([go, "test", "./..."], cwd=package, env=env)
    _skip_for_missing_offline_dependency(
        result,
        markers=(
            "module lookup disabled by goproxy=off",
            "missing go.sum entry",
            "no required module provides package",
        ),
    )
    _assert_success(result)


def test_generated_rust_sources_are_rustfmt_clean_when_available(tmp_path: Path) -> None:
    rustfmt = shutil.which("rustfmt")
    if rustfmt is None:
        pytest.skip("rustfmt is not installed")

    package = _generate(tmp_path, "rust")
    sources = sorted(str(path) for path in (package / "src").rglob("*.rs"))
    assert sources
    result = _run([rustfmt, "--check", *sources], cwd=package)
    _assert_success(result)


def test_generated_rust_package_checks_offline_when_dependencies_are_cached(
    tmp_path: Path,
) -> None:
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is not installed")

    package = _generate(tmp_path, "rust")
    result = _run([cargo, "check", "--offline"], cwd=package)
    _skip_for_missing_offline_dependency(
        result,
        markers=(
            "no matching package named",
            "failed to download",
            "attempting to make an http request",
        ),
    )
    _assert_success(result)
