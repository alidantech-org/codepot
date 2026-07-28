from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from click.testing import CliRunner
from dryv.api import OperationResult, OperationStatus
from dryv.generation import GenerationData, GenerationPlan

from dryv_cli.app import app


@dataclass
class FakeRuntime:
    plan_called: bool = False
    write_called: bool = False

    def plan(self, project: Path) -> OperationResult[GenerationData]:
        self.plan_called = True
        return _ready_result()

    def generate_to_files(
        self,
        project: Path,
        *,
        destination: Path | None = None,
    ) -> tuple[OperationResult[GenerationData], None]:
        self.write_called = True
        return _ready_result(), None


def test_non_interactive_generation_never_waits_for_a_prompt(monkeypatch) -> None:
    runtime = FakeRuntime()
    monkeypatch.setattr("dryv_cli.commands.generate.acquire_runtime", lambda **_: runtime)
    monkeypatch.setattr("dryv_cli.commands.generate.can_prompt", lambda: False)

    result = CliRunner().invoke(app, ["generate", "project.yaml", "--json"])

    assert result.exit_code == 0
    assert runtime.plan_called is False
    assert runtime.write_called is True
    assert '"status": "ready"' in result.output


def test_forced_confirmation_fails_cleanly_without_a_tty(monkeypatch) -> None:
    runtime = FakeRuntime()
    monkeypatch.setattr("dryv_cli.commands.generate.acquire_runtime", lambda **_: runtime)
    monkeypatch.setattr("dryv_cli.commands.generate.can_prompt", lambda: False)

    result = CliRunner().invoke(app, ["generate", "project.yaml", "--confirm"])

    assert result.exit_code == 2
    assert runtime.plan_called is False
    assert runtime.write_called is False
    assert "PROMPT_UNAVAILABLE" in result.output


def _ready_result() -> OperationResult[GenerationData]:
    return OperationResult(
        status=OperationStatus.READY,
        data=GenerationData(
            plan=GenerationPlan(project_name="example", artifacts=()),
        ),
        operation_id="operation-1",
    )
