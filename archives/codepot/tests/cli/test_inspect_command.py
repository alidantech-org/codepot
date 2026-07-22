from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_inspect_overview() -> None:
    result = runner.invoke(app, ["inspect"])

    assert result.exit_code == 0
    assert "Inspect" in result.output
    assert "codepot.v1.yaml" in result.output
    assert "Title" in result.output
    assert "Demo API" in result.output
    assert "Project key" in result.output
    assert "demo_api" in result.output
    assert "Spec version" in result.output
    assert "API version" in result.output
    assert "Codepot IR" in result.output
    assert "Content types" in result.output
    assert "13" in result.output
    assert "Resources" in result.output
    assert "3" in result.output


def test_inspect_schemas_mode() -> None:
    result = runner.invoke(app, ["inspect", "--schemas"])

    assert result.exit_code == 0
    assert "Schemas" in result.output
    assert "entities" in result.output
    assert "field_sets" in result.output
    assert "models" in result.output
    assert "dtos" in result.output


def test_inspect_resources_mode() -> None:
    result = runner.invoke(app, ["inspect", "--resources"])

    assert result.exit_code == 0
    assert "Resources" in result.output
    assert "users" in result.output
    assert "posts" in result.output
    assert "tenants" in result.output


def test_inspect_content_types_mode() -> None:
    result = runner.invoke(app, ["inspect", "--content-types"])

    assert result.exit_code == 0
    assert "Content Types" in result.output
    assert "json" in result.output
    assert "application/json" in result.output


def test_inspect_rejects_multiple_modes() -> None:
    result = runner.invoke(app, ["inspect", "--schemas", "--refs"])

    assert result.exit_code == 3
    assert "Choose only one inspect mode flag." in result.output
