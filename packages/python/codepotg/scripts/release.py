"""Build, validate, smoke-test, and optionally publish CodepotG.

The script deliberately keeps publishing separate from normal package commands.
It reads ``PUBLISH_TOKEN`` from the environment or the ignored local ``.env``
file and never prints the credential.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv
import zipfile
from pathlib import Path
from typing import NoReturn

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PACKAGE_ROOT / "dist"
EXPECTED_VERSION = "1.0.0"
CONFIG_NAME = "Codepotg.yaml"
LEGACY_CONFIG_NAMES = ("CodepotFile.yml", "CodepotFile.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or publish codepotg 1.0.0.")
    parser.add_argument(
        "action",
        choices=("check", "publish"),
        help=(
            "Run all checks, or run all checks and upload the exact artifacts "
            "to PyPI."
        ),
    )
    arguments = parser.parse_args()

    verify_source_metadata()
    clean_build_artifacts()
    run(sys.executable, "-m", "pytest")
    run(sys.executable, "-m", "ruff", "check", ".")
    run(sys.executable, "-m", "build")

    artifacts = select_artifacts()
    run(sys.executable, "-m", "twine", "check", *map(str, artifacts))

    wheel = next(path for path in artifacts if path.suffix == ".whl")
    source_distribution = next(
        path for path in artifacts if path.name.endswith(".tar.gz")
    )
    inspect_wheel(wheel)
    inspect_source_distribution(source_distribution)
    smoke_test_wheel(wheel)

    print(f"Release checks passed for codepotg {EXPECTED_VERSION}.")

    if arguments.action == "publish":
        upload_to_pypi(artifacts)


def verify_source_metadata() -> None:
    pyproject_path = PACKAGE_ROOT / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = pyproject.get("project", {})
    metadata_version = project.get("version")
    if metadata_version != EXPECTED_VERSION:
        fail(
            f"pyproject.toml version is {metadata_version!r}, "
            f"expected {EXPECTED_VERSION!r}."
        )

    init_path = PACKAGE_ROOT / "src" / "codepotg" / "__init__.py"
    init_text = init_path.read_text(encoding="utf-8")
    match = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        init_text,
        re.MULTILINE,
    )
    if match is None or match.group(1) != EXPECTED_VERSION:
        fail("codepotg.__version__ is missing or does not match 1.0.0.")

    constants_path = PACKAGE_ROOT / "cli" / "constants" / "constants.py"
    constants_text = constants_path.read_text(encoding="utf-8")
    match = re.search(
        r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']',
        constants_text,
        re.MULTILINE,
    )
    if match is None or match.group(1) != EXPECTED_VERSION:
        fail("CLI APP_VERSION is missing or does not match 1.0.0.")

    required_files = (
        "README.md",
        "RELEASE.md",
        "CHANGELOG.md",
        "LICENSE",
        "MANIFEST.in",
    )
    for required in required_files:
        if not (PACKAGE_ROOT / required).is_file():
            fail(f"Required release file is missing: {required}")

    verify_config_contract(constants_text)


def verify_config_contract(constants_text: str) -> None:
    loader_path = PACKAGE_ROOT / "src" / "codepot_file" / "loader.py"
    loader_text = loader_path.read_text(encoding="utf-8")
    if f'CODEPOTG_CONFIG_NAME = "{CONFIG_NAME}"' not in loader_text:
        fail(f"The runtime does not declare {CONFIG_NAME} as its canonical config.")

    for legacy_name in LEGACY_CONFIG_NAMES:
        if legacy_name not in loader_text:
            fail(f"The runtime does not explicitly guard legacy config {legacy_name}.")

    if CONFIG_NAME not in constants_text:
        fail(f"CLI help does not mention the canonical {CONFIG_NAME} config.")

    for document in ("README.md", "RELEASE.md", "CHANGELOG.md"):
        text = (PACKAGE_ROOT / document).read_text(encoding="utf-8")
        if CONFIG_NAME not in text:
            fail(f"{document} does not document {CONFIG_NAME}.")


def clean_build_artifacts() -> None:
    for directory in (DIST_DIR, PACKAGE_ROOT / "build"):
        if directory.exists():
            shutil.rmtree(directory)

    for pattern in ("*.egg-info", "src/*.egg-info"):
        for directory in PACKAGE_ROOT.glob(pattern):
            if directory.is_dir():
                shutil.rmtree(directory)


def select_artifacts() -> list[Path]:
    artifacts = sorted(path for path in DIST_DIR.glob("*") if path.is_file())
    if len(artifacts) != 2:
        fail(f"Expected exactly two release artifacts, found {len(artifacts)}.")

    wheels = [path for path in artifacts if path.suffix == ".whl"]
    source_distributions = [
        path for path in artifacts if path.name.endswith(".tar.gz")
    ]
    if len(wheels) != 1 or len(source_distributions) != 1:
        fail("Expected one wheel and one .tar.gz source distribution.")

    wheel = wheels[0]
    source_distribution = source_distributions[0]
    expected_wheel_suffix = f"-{EXPECTED_VERSION}-py3-none-any.whl"
    if not wheel.name.endswith(expected_wheel_suffix):
        fail(f"Expected a universal wheel, received: {wheel.name}")
    if source_distribution.name != f"codepotg-{EXPECTED_VERSION}.tar.gz":
        fail(f"Unexpected source distribution name: {source_distribution.name}")
    return artifacts


def inspect_wheel(wheel: Path) -> None:
    required_members = {
        "codepotg/__init__.py",
        "codepotg/__main__.py",
        "codepotg/cli/main.py",
        "app/__init__.py",
        "cli/main.py",
        "openapi/loader.py",
        "codepotg/templates/debug/paths.yaml",
        "codepotg/templates/typescript/paths.yaml",
        "codepotg/templates/next/paths.yaml",
        "codepotg/templates/dart/paths.yaml",
    }

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        reject_secret_members(names)
        missing = sorted(required_members - names)
        if missing:
            fail("Wheel is missing required runtime files:\n  - " + "\n  - ".join(missing))

        metadata_name = next(
            (name for name in names if name.endswith(".dist-info/METADATA")),
            None,
        )
        entries_name = next(
            (name for name in names if name.endswith(".dist-info/entry_points.txt")),
            None,
        )
        license_name = next(
            (name for name in names if name.endswith(".dist-info/licenses/LICENSE")),
            None,
        )
        if not metadata_name or not entries_name or not license_name:
            fail("Wheel metadata, console entry points, or license file is incomplete.")

        metadata = archive.read(metadata_name).decode("utf-8")
        entries = archive.read(entries_name).decode("utf-8")
        if f"Version: {EXPECTED_VERSION}" not in metadata:
            fail("Wheel METADATA does not report version 1.0.0.")
        if "License-Expression: MIT" not in metadata:
            fail("Wheel METADATA does not report the MIT SPDX license expression.")
        if "codepotg = codepotg.cli.main:app" not in entries:
            fail("Wheel does not expose the expected codepotg console script.")

        jinja_templates = [name for name in names if name.endswith(".j2")]
        if not jinja_templates:
            fail("Wheel contains no bundled Jinja templates.")


def inspect_source_distribution(source_distribution: Path) -> None:
    prefix = f"codepotg-{EXPECTED_VERSION}/"
    required_members = {
        f"{prefix}README.md",
        f"{prefix}RELEASE.md",
        f"{prefix}CHANGELOG.md",
        f"{prefix}LICENSE",
        f"{prefix}MANIFEST.in",
        f"{prefix}pyproject.toml",
        f"{prefix}src/codepotg/__init__.py",
        f"{prefix}src/codepotg/templates/typescript/paths.yaml",
        f"{prefix}tests/fixtures/sample_openapi.yaml",
    }

    with tarfile.open(source_distribution, "r:gz") as archive:
        names = set(archive.getnames())
        reject_secret_members(names)
        missing = sorted(required_members - names)
        if missing:
            fail(
                "Source distribution is missing required files:\n  - "
                + "\n  - ".join(missing)
            )


def reject_secret_members(names: set[str]) -> None:
    forbidden = [name for name in names if Path(name).name in {".env", ".pypirc"}]
    if forbidden:
        fail("Release artifacts contain secret configuration files: " + ", ".join(forbidden))


def smoke_test_wheel(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="codepotg-release-") as temporary:
        temporary_root = Path(temporary)
        environment_root = temporary_root / "venv"
        project_root = temporary_root / "project"
        project_root.mkdir()

        venv.EnvBuilder(with_pip=True, clear=True).create(environment_root)
        scripts_directory = environment_root / ("Scripts" if os.name == "nt" else "bin")
        python = scripts_directory / ("python.exe" if os.name == "nt" else "python")
        executable = scripts_directory / ("codepotg.exe" if os.name == "nt" else "codepotg")

        run(
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            str(wheel),
        )
        run(
            str(python),
            "-c",
            (
                "import codepotg; "
                f"assert codepotg.__version__ == '{EXPECTED_VERSION}', "
                "codepotg.__version__"
            ),
        )
        run(str(executable), "--version", expected=f"codepotg {EXPECTED_VERSION}")
        run(str(executable), "--help")
        run(
            str(python),
            "-m",
            "codepotg",
            "--version",
            expected=f"codepotg {EXPECTED_VERSION}",
        )

        run(str(executable), "init", "--yes", working_directory=project_root)
        verify_generated_config(project_root)

        fixture = PACKAGE_ROOT / "tests" / "fixtures" / "sample_openapi.yaml"
        shutil.copyfile(fixture, project_root / "openapi.yaml")
        run(
            str(executable),
            "generate",
            "sdk",
            "--dry-run",
            "--verbose",
            expected="Completed 1 task(s).",
            working_directory=project_root,
        )


def verify_generated_config(project_root: Path) -> None:
    config = project_root / CONFIG_NAME
    if not config.is_file():
        fail(f"Installed CLI did not create {CONFIG_NAME}.")

    for legacy_name in LEGACY_CONFIG_NAMES:
        if (project_root / legacy_name).exists():
            fail(f"Installed CLI unexpectedly created legacy config {legacy_name}.")

    content = config.read_text(encoding="utf-8")
    if "templateDir:" in content or "templates:" in content:
        fail("Starter config must use bundled templates without a custom template path.")
    for required in ("allow: true", "input: ./openapi.yaml", "language: typescript"):
        if required not in content:
            fail(f"Starter config is missing expected content: {required}")


def upload_to_pypi(artifacts: list[Path]) -> None:
    token = read_publish_token()
    environment = os.environ.copy()
    environment["TWINE_USERNAME"] = "__token__"
    environment["TWINE_PASSWORD"] = token

    print(f"Uploading codepotg {EXPECTED_VERSION} to PyPI...")
    run(
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--non-interactive",
        *map(str, artifacts),
        environment=environment,
    )
    print(f"Published codepotg {EXPECTED_VERSION} to PyPI.")


def read_publish_token() -> str:
    value = os.environ.get("PUBLISH_TOKEN", "").strip()
    if not value:
        value = read_dotenv_token()
    if not value:
        fail("PUBLISH_TOKEN is not set in the environment or local .env file.")
    if not value.startswith("pypi-"):
        fail("PUBLISH_TOKEN does not look like a PyPI API token.")
    return value


def read_dotenv_token() -> str:
    dotenv = PACKAGE_ROOT / ".env"
    if not dotenv.is_file():
        return ""

    for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, raw_value = line.partition("=")
        if separator and key.strip() == "PUBLISH_TOKEN":
            return raw_value.strip().strip('"\'')
    return ""


def run(
    *command: str,
    expected: str | None = None,
    environment: dict[str, str] | None = None,
    working_directory: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    printable = " ".join(command)
    print(f"+ {printable}")
    result = subprocess.run(
        command,
        cwd=working_directory or PACKAGE_ROOT,
        env=environment,
        check=False,
        text=True,
        capture_output=expected is not None,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        fail(f"Command failed with exit code {result.returncode}: {printable}")
    if expected is not None:
        output = f"{result.stdout}\n{result.stderr}".strip()
        if expected not in output:
            fail(f"Expected {expected!r} in command output, received:\n{output}")
    return result


def fail(message: str) -> NoReturn:
    raise SystemExit(f"Release check failed: {message}")


if __name__ == "__main__":
    main()
