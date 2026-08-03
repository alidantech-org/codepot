from pathlib import Path

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_emit_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr("cli.options.ask_spec_path", lambda default: Path("codepot.v1.yaml"))
    monkeypatch.setattr("cli.options.ask_language", lambda default: "typescript")
    monkeypatch.setattr(
        "cli.options.ask_template_package_path",
        lambda default: Path("templates/typescript"),
    )
    monkeypatch.setattr("cli.options.ask_output_path", lambda default: Path("generated/typescript"))
    monkeypatch.setattr("cli.options.ask_select", lambda optional=True: None)
    monkeypatch.setattr("cli.options.ask_template_ids", lambda: ())
    monkeypatch.setattr("cli.options.ask_dry_run", lambda default: True)
    monkeypatch.setattr("cli.options.ask_force", lambda default: default)
    monkeypatch.setattr("cli.options.ask_format", lambda default: default)
    monkeypatch.setattr("cli.options.ask_run_hooks", lambda default: default)
    monkeypatch.setattr("cli.options.ask_skip_static", lambda default: default)

    result = runner.invoke(app, ["emit", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Dry run typescript -> generated/typescript" in result.output
