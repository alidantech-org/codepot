from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _tsc() -> str:
    executable = shutil.which("tsc")
    if executable is None:
        pytest.skip("tsc is not installed")
    return executable


@pytest.mark.oracle
def test_optional_tsc_version_and_representative_fixtures(tmp_path: Path) -> None:
    executable = _tsc()
    version = subprocess.run(
        [executable, "--version"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert version.stdout.startswith("Version ")

    (tmp_path / "user.ts").write_text(
        "export interface User { readonly user_id: string }\n",
        encoding="utf-8",
    )
    (tmp_path / "service.ts").write_text(
        (
            'import type { User } from "./user";\n'
            "const $user: User = { user_id: '1' };\n"
            "const _private = $user.user_id;\n"
            "export { $user, _private };\n"
        ),
        encoding="utf-8",
    )
    valid = subprocess.run(
        [
            executable,
            "--noEmit",
            "--strict",
            "--module",
            "node16",
            "--moduleResolution",
            "node16",
            str(tmp_path / "service.ts"),
            str(tmp_path / "user.ts"),
        ],
        capture_output=True,
        text=True,
    )
    assert valid.returncode == 0, valid.stdout + valid.stderr

    (tmp_path / "invalid.ts").write_text("const class = 1;\n", encoding="utf-8")
    invalid = subprocess.run(
        [executable, "--noEmit", str(tmp_path / "invalid.ts")],
        capture_output=True,
        text=True,
    )
    assert invalid.returncode != 0
