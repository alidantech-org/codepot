from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_infer_lists_planned_files() -> None:
    result = runner.invoke(app, ["infer"])

    assert result.exit_code == 0
    assert "Infer  codepot.v1.yaml" in result.output
    assert "typescript" in result.output
    assert "src/models/user.ts" in result.output
    assert "src/dtos/users/dtos.ts" in result.output
    assert "src/index.ts" in result.output
    assert "No files written. Run emit to generate." in result.output


def test_infer_show_paths_outputs_paths_only() -> None:
    result = runner.invoke(app, ["infer", "--show-paths"])

    assert result.exit_code == 0
    assert result.output.splitlines() == [
        "src/models/user.ts",
        "src/dtos/users/dtos.ts",
        "src/index.ts",
    ]


def test_infer_filters_by_select() -> None:
    result = runner.invoke(app, ["infer", "--select", "models.each"])

    assert result.exit_code == 0
    assert "src/models/user.ts" in result.output
    assert "src/dtos/users/dtos.ts" not in result.output


def test_infer_filters_by_template_aliases() -> None:
    result = runner.invoke(
        app,
        ["infer", "--template", "model_files", "--only", "index"],
    )

    assert result.exit_code == 0
    assert "src/models/user.ts" in result.output
    assert "src/index.ts" in result.output
    assert "src/dtos/users/dtos.ts" not in result.output


def test_infer_shows_imports_and_dependencies() -> None:
    result = runner.invoke(app, ["infer", "--show-imports", "--show-dependencies"])

    assert result.exit_code == 0
    assert "Imports" in result.output
    assert "UserRole" in result.output
    assert "Dependencies" in result.output
    assert "resolves enums" in result.output
