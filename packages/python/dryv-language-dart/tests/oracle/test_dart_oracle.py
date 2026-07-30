from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _dart() -> str:
    executable = shutil.which("dart")
    if executable is None:
        pytest.skip("Dart SDK is not installed")
    return executable


@pytest.mark.oracle
def test_optional_dart_version_and_representative_fixtures(tmp_path: Path) -> None:
    executable = _dart()
    version = subprocess.run(
        [executable, "--version"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "Dart SDK version" in version.stdout + version.stderr

    lib = tmp_path / "lib" / "src"
    lib.mkdir(parents=True)
    (tmp_path / "pubspec.yaml").write_text(
        "name: oracle_fixture\nenvironment:\n  sdk: '>=3.0.0 <4.0.0'\n",
        encoding="utf-8",
    )
    (lib / "user.dart").write_text(
        "class User { const User(this.userId); final String userId; }\n",
        encoding="utf-8",
    )
    (lib / "service.dart").write_text(
        (
            "import './user.dart';\n"
            "final _private = const User('1');\n"
            "User makeUser() => _private;\n"
        ),
        encoding="utf-8",
    )
    valid = subprocess.run(
        [executable, "analyze", str(lib)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert valid.returncode == 0, valid.stdout + valid.stderr

    invalid = lib / "invalid.dart"
    invalid.write_text("final class = 1;\n", encoding="utf-8")
    rejected = subprocess.run(
        [executable, "analyze", str(invalid)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
