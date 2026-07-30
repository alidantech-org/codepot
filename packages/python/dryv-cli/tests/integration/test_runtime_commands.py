from __future__ import annotations

from click.testing import CliRunner
from dryv import DryvRuntime, RuntimePlugins

from dryv_cli.app import app


def test_version_reports_cli_and_runtime_versions() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "dryv-cli" in result.output
    assert "runtime" in result.output


def test_plugins_command_renders_the_public_runtime_snapshot(monkeypatch) -> None:
    runtime = DryvRuntime(plugins=RuntimePlugins())
    monkeypatch.setattr("dryv_cli.commands.plugins.acquire_runtime", lambda **_: runtime)

    result = CliRunner().invoke(app, ["plugins"])

    assert result.exit_code == 0
    assert "runtime" in result.output
    assert "no optional plugins loaded" in result.output


def test_plugins_json_is_machine_readable(monkeypatch) -> None:
    runtime = DryvRuntime(plugins=RuntimePlugins())
    monkeypatch.setattr("dryv_cli.commands.plugins.acquire_runtime", lambda **_: runtime)

    result = CliRunner().invoke(app, ["plugins", "--json"])

    assert result.exit_code == 0
    assert '"coreVersion"' in result.output
    assert '"plugins": []' in result.output
    assert "\x1b[" not in result.output
