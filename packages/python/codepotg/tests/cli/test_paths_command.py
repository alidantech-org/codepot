from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cli.main import app


def test_paths_command_lists_resolved_folder_recipes(tmp_path: Path) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    (template_root / "paths.yml").write_text(
        """
imports:
  strategy: relative
folders:
  dto:
    select: schemas.emit_dtos
    as: dto
    mode: each
    parts:
      - src
      - dto
""".strip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["paths", str(template_root)])

    assert result.exit_code == 0, result.output
    assert "Resolved:" in result.output
    assert "paths.yml" in result.output
    assert "dto: select=schemas.emit_dtos" in result.output
    assert "as=dto" in result.output
    assert "parts=src/dto" in result.output


def test_paths_command_reports_unknown_keys(tmp_path: Path) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    (template_root / "paths.yaml").write_text(
        """
folders:
  dto:
    select: schemas.emit_dtos
    parts: [src]
    depends_on: [enum]
""".strip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["paths", str(template_root)])

    assert result.exit_code == 1
    assert "Unknown key" in result.output
    assert "depends_on" in result.output
