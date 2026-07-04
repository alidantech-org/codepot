from __future__ import annotations

from typer.testing import CliRunner

from cli.main import app


def test_generate_missing_config_file_fails_with_helpful_message() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["generate"])

    assert result.exit_code == 1
    assert "CodepotFile.yml not found" in result.output


def test_help_only_exposes_generate_command() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "generate" in result.output
    assert "emit" not in result.output
    assert "infer" not in result.output
    assert "inspect" not in result.output
    assert "validate" not in result.output


def test_emit_command_is_not_public() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["emit", "--help"])

    assert result.exit_code != 0
    assert "No such command" in result.output
