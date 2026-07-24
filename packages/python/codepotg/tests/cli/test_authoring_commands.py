from __future__ import annotations

from typer.testing import CliRunner

from cli.main import app


def test_help_exposes_jsonl_and_paths_authoring_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "jsonl" in result.output
    assert "paths" in result.output
