from pathlib import Path

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_inspect_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr("cli.options.ask_spec_path", lambda default: Path("codepot.v1.yaml"))
    monkeypatch.setattr("cli.options.ask_inspect_mode", lambda: "overview")

    result = runner.invoke(app, ["inspect", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Codepot Spec" in result.output
