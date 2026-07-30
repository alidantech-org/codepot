from __future__ import annotations

from click.testing import CliRunner

from dryv_cli.app import app


def test_root_help_uses_a_readable_command_tree_without_panels() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Dryv" in result.output
    assert "├─" in result.output
    assert "└─" in result.output
    assert "plan" in result.output
    assert "generate" in result.output
    assert "plugins" in result.output
    assert "┌" not in result.output
    assert "┐" not in result.output
    assert "└────" not in result.output


def test_command_help_remains_borderless() -> None:
    result = CliRunner().invoke(app, ["generate", "--help"])

    assert result.exit_code == 0
    assert "generate" in result.output
    assert "--memory" in result.output
    assert "--destination" in result.output
    assert "┌" not in result.output
    assert "┐" not in result.output
