from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_validate_uses_default_spec_path() -> None:
    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "Validate" in result.output
    assert "codepot.v1.yaml" in result.output
    assert "Spec file found" in result.output
    assert "YAML parsed" in result.output
    assert "Pydantic validation passed" in result.output
    assert "Repository built" in result.output
    assert "Required sections present" in result.output
    assert "Spec is valid." in result.output


def test_validate_json_output() -> None:
    result = runner.invoke(app, ["validate", "--json"])

    assert result.exit_code == 0
    assert '"spec_path": "codepot.v1.yaml"' in result.output
    assert '"metadata": {' in result.output
    assert '"counts": {' in result.output
    assert '"ok": true' in result.output
