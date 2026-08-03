from __future__ import annotations

from pathlib import Path

from archives.codepotg.cli.main import app
from typer.testing import CliRunner


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
    assert "Legacy Folder Recipes" in result.output
    assert "dto: select=schemas.emit_dtos" in result.output
    assert "as=dto" in result.output
    assert "parts=src/dto" in result.output
    assert "Selections: none" in result.output
    assert "Emissions: none" in result.output
    assert "Barrels: none" in result.output


def test_paths_command_lists_selection_emission_provider_and_barrel_graph(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    for name in ("dto.ts.j2", "enum.ts.j2", "operation.ts.j2", "index.ts.j2"):
        (template_root / name).write_text("generated\n", encoding="utf-8")
    (template_root / "paths.yaml").write_text(
        """
selections:
  dtos:
    select: schemas.emit_dtos
    as: dto
  enums:
    select: schemas.emit_enums
    as: enum
  operations:
    select: operations
    as: operation

emissions:
  dto-types:
    selection: dtos
    template: dto.ts.j2
    output: [models, "[dto.name.path.o].ts"]
    provides: [dtos]
  enum-types:
    selection: enums
    template: enum.ts.j2
    output: [models, "[enum.name.path.o].ts"]
    provides: [enums]
  operations:
    selection: operations
    template: operation.ts.j2
    output: [operations, "[operation.name.path.o].ts"]
    imports:
      dtos: dto-types
      enums: enum-types

barrels:
  models:
    template: index.ts.j2
    output: [models, index.ts]
    exports: [dto-types, enum-types]
""".strip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["paths", str(template_root)])

    assert result.exit_code == 0, result.output
    assert "Selections" in result.output
    assert "dtos: select=schemas.emit_dtos; as=dto; scope=each" in result.output
    assert "Emissions" in result.output
    assert "dto-types: selection=dtos; template=dto.ts.j2" in result.output
    assert "providers=dtos=dto-types, enums=enum-types" in result.output
    assert "Barrels" in result.output
    assert "models: template=index.ts.j2" in result.output
    assert "exports=dto-types, enum-types" in result.output


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


def test_paths_command_reports_graph_reference_errors(tmp_path: Path) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    (template_root / "dto.ts.j2").write_text("generated\n", encoding="utf-8")
    (template_root / "paths.yaml").write_text(
        """
selections:
  dtos:
    select: schemas.emit_dtos
emissions:
  dto-types:
    selection: missing
    template: dto.ts.j2
    output: [models, dto.ts]
""".strip(),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["paths", str(template_root)])

    assert result.exit_code == 1
    assert "unknown selection 'missing'" in result.output
