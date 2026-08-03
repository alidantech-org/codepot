from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_emit_dry_run_lists_planned_files() -> None:
    result = runner.invoke(app, ["emit", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run typescript -> generated/typescript" in result.output
    assert "planned" in result.output
    assert "generated/typescript/src/models/user.ts" in result.output
    assert "generated/typescript/src/dtos/users/dtos.ts" in result.output
    assert "generated/typescript/src/index.ts" in result.output
    assert "3 files processed" in result.output


def test_emit_watch_fails_as_config_error() -> None:
    result = runner.invoke(app, ["emit", "--watch"])

    assert result.exit_code == 3
    assert "--watch is not implemented yet." in result.output


def test_emit_filters_by_select_and_template() -> None:
    result = runner.invoke(
        app,
        ["emit", "--dry-run", "--select", "models.each", "--template", "model_files"],
    )

    assert result.exit_code == 0
    assert "generated/typescript/src/models/user.ts" in result.output
    assert "generated/typescript/src/dtos/users/dtos.ts" not in result.output


def test_emit_shows_fake_formatters_and_hooks() -> None:
    result = runner.invoke(app, ["emit", "--dry-run", "--format", "--run-hooks"])

    assert result.exit_code == 0
    assert "Formatter" in result.output
    assert "Would run: pnpm prettier --write ." in result.output
    assert "Hooks" in result.output
    assert "Would run: pnpm tsc --noEmit" in result.output
