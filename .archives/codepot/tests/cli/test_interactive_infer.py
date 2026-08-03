from pathlib import Path

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_infer_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr("cli.options.ask_spec_path", lambda default: Path("codepot.v1.yaml"))
    monkeypatch.setattr("cli.options.ask_language", lambda default: "typescript")
    monkeypatch.setattr(
        "cli.options.ask_template_package_path",
        lambda default: Path("templates/typescript"),
    )
    monkeypatch.setattr("cli.options.ask_output_path", lambda default: Path("generated/typescript"))
    monkeypatch.setattr("cli.options.ask_select", lambda optional=True: None)
    monkeypatch.setattr("cli.options.ask_template_ids", lambda: ())
    monkeypatch.setattr("cli.options.ask_show_paths", lambda default: default)
    monkeypatch.setattr("cli.options.ask_show_context", lambda default: default)
    monkeypatch.setattr("cli.options.ask_show_imports", lambda default: default)
    monkeypatch.setattr("cli.options.ask_show_dependencies", lambda default: default)

    result = runner.invoke(app, ["infer", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Infer  codepot.v1.yaml" in result.output
