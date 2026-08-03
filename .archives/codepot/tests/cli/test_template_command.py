from pathlib import Path

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_template_validate_command() -> None:
    result = runner.invoke(app, ["template", "validate"])

    assert result.exit_code == 0
    assert "Template Validate" in result.output
    assert "Template package is valid." in result.output


def test_template_inspect_command() -> None:
    result = runner.invoke(app, ["template", "inspect"])

    assert result.exit_code == 0
    assert "Template Package" in result.output
    assert "model_files" in result.output
    assert "dto_files" in result.output


def test_template_vars_command() -> None:
    result = runner.invoke(app, ["template", "vars", "--select", "models.each"])

    assert result.exit_code == 0
    assert "Template Variables  models.each" in result.output
    assert "model.fields[]" in result.output
    assert "dependencies.enums[]" in result.output


def test_template_vars_requires_select() -> None:
    result = runner.invoke(app, ["template", "vars"])

    assert result.exit_code == 3
    assert "Missing required option: --select" in result.output


def test_template_selections_command() -> None:
    result = runner.invoke(app, ["template", "selections"])

    assert result.exit_code == 0
    assert "Valid selections" in result.output
    assert "models.each" in result.output
    assert "once" in result.output


def test_template_validate_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr(
        "cli.options.ask_template_package_path",
        lambda default: Path("templates/typescript"),
    )

    result = runner.invoke(app, ["template", "validate", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Template package is valid." in result.output


def test_template_vars_interactive_short_option(monkeypatch) -> None:
    monkeypatch.setattr(
        "cli.options.ask_template_package_path",
        lambda default: Path("templates/typescript"),
    )
    monkeypatch.setattr("cli.options.ask_select", lambda optional=True: "models.each")

    result = runner.invoke(app, ["template", "vars", "-I"])

    assert result.exit_code == 0
    assert "No such option" not in result.output
    assert "Template Variables  models.each" in result.output
