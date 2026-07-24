from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from app.models import EmitOutput
from app.workflows import generate as generate_workflow
from cli.main import app


def test_generate_reports_explicit_yml_config_name(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    config = tmp_path / "Codepotg.yml"
    config.write_text(
        """
allow: true
tasks:
  sdk:
    input: ./openapi.yaml
    language: typescript
    output: ./generated
""".strip(),
        encoding="utf-8",
    )

    def fake_emit(request):
        return EmitOutput(
            input_path=request.input_path,
            language=request.language,
            output_path=request.output_path,
            dry_run=request.dry_run,
            planned=[request.output_path / "planned.ts"],
        )

    monkeypatch.setattr(generate_workflow, "run_emit", fake_emit)

    result = runner.invoke(app, ["generate", "--config", str(config)])

    assert result.exit_code == 0
    assert "Loading Codepotg.yml" in result.output
    assert "Loading Codepotg.yaml" not in result.output
