from __future__ import annotations

from typer.testing import CliRunner

from codepotg.cli.main import app


def test_cli_reports_release_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "codepotg 1.0.0"
