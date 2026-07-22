from pathlib import Path

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_validate_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr("cli.options.ask_spec_path", lambda default: Path("codepot.v1.yaml"))
    monkeypatch.setattr("cli.options.ask_strict", lambda default: default)

    result = runner.invoke(app, ["validate", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Spec is valid." in result.output
