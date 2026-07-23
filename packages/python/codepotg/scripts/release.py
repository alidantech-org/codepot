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
import tempfile
import tomllib
import venv
import zipfile
from pathlib import Path
from typing import NoReturn

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PACKAGE_ROOT / "dist"
EXPECTED_VERSION = "1.0.0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or publish codepotg 1.0.0.")
    parser.add_argument(
        "action",
        choices=("check", "publish"),
        help="Run all checks, or run all checks and upload the exact artifacts to PyPI.",
    )
    arguments = parser.parse_args()

    verify_source_metadata()
    clean_build_artifacts()
    run(sys.executable, "-m", "pytest")
    run(sys.executable, "-m", "ruff", "check", ".")
    run(sys.executable, "-m", "build")

    artifacts = sorted(DIST_DIR.glob("*"))
    if not artifacts:
        fail("No distributions were created in dist/.")

    run(sys.executable, "-m", "twine", "check", *map(str, artifacts))
    wheel = select_wheel(artifacts)
    inspect_wheel(wheel)
    smoke_test_wheel(wheel)

    print(f"Release checks passed for codepotg {EXPECTED_VERSION}.")

    if arguments.action == "publish":
        upload_to_pypi(artifacts)


def verify_source_metadata() -> None:
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject.get("project", {})
    metadata_version = project.get("version")
    if metadata_version != EXPECTED_VERSION:
        fail(f"pyproject.toml version is {metadata_version!r}, expected {EXPECTED_VERSION!r}.")

    init_text = (PACKAGE_ROOT / "src" / "codepotg" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.MULTILINE)
    if match is None or match.group(1) != EXPECTED_VERSION:
        fail("codepotg.__version__ is missing or does not match 1.0.0.")

    constants_text = (PACKAGE_ROOT / "cli" / "constants" / "constants.py").read_text(
        encoding="utf-8"
    )
    match = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', constants_text, re.MULTILINE)
    if match is None or match.group(1) != EXPECTED_VERSION:
        fail("CLI APP_VERSION is missing or does not match 1.0.0.")

    for required in ("README.md", "LICENSE", "MANIFEST.in"):
        if not (PACKAGE_ROOT / required).is_file():
            fail(f"Required release file is missing: {required}")


def clean_build_artifacts() -> None:
    for directory in (DIST_DIR, PACKAGE_ROOT / "build"):
        if directory.exists():
            shutil.rmtree(directory)

    for pattern in ("*.egg-info", "src/*.egg-info"):
        for directory in PACKAGE_ROOT.glob(pattern):
            if directory.is_dir():
                shutil.rmtree(directory)


def select_wheel(artifacts: list[Path]) -> Path:
    wheels = [path for path in artifacts if path.suffix == ".whl"]
    if len(wheels) != 1:
        fail(f"Expected exactly one wheel, found {len(wheels)}.")
    wheel = wheels[0]
    if f"-{EXPECTED_VERSION}-" not in wheel.name:
        fail(f"Unexpected wheel version in filename: {wheel.name}")
    return wheel


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
        missing = sorted(required_members - names)
        if missing:
            fail("Wheel is missing required runtime files:\n  - " + "\n  - ".join(missing))

        metadata_name = next((name for name in names if name.endswith(".dist-info/METADATA")), None)
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
        if "codepotg = codepotg.cli.main:app" not in entries:
            fail("Wheel does not expose the expected codepotg console script.")

        jinja_templates = [name for name in names if name.endswith(".j2")]
        if not jinja_templates:
            fail("Wheel contains no bundled Jinja templates.")


def smoke_test_wheel(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="codepotg-release-") as temporary:
        environment_root = Path(temporary) / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment_root)
        python = environment_root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        executable = environment_root / ("Scripts/codepotg.exe" if os.name == "nt" else "bin/codepotg")

        run(str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel))
        run(
            str(python),
            "-c",
            (
                "import codepotg; "
                f"assert codepotg.__version__ == '{EXPECTED_VERSION}', codepotg.__version__"
            ),
        )
        run(str(executable), "--version", expected=f"codepotg {EXPECTED_VERSION}")
        run(str(executable), "--help")
        run(str(python), "-m", "codepotg", "--version", expected=f"codepotg {EXPECTED_VERSION}")


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
    if value:
        return value

    dotenv = PACKAGE_ROOT / ".env"
    if dotenv.is_file():
        for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            key, separator, raw_value = line.partition("=")
            if separator and key.strip() == "PUBLISH_TOKEN":
                value = raw_value.strip().strip('"\'')
                if value:
                    return value

    fail("PUBLISH_TOKEN is not set in the environment or local .env file.")


def run(
    *command: str,
    expected: str | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    printable = " ".join(command)
    print(f"+ {printable}")
    result = subprocess.run(
        command,
        cwd=PACKAGE_ROOT,
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
