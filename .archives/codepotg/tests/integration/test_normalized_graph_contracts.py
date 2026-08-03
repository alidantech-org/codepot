from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp


def test_graph_templates_render_real_normalized_entity_and_frontend_roots(
    tmp_path: Path,
    real_openapi_json_path: Path,
) -> None:
    project = tmp_path / "normalized-graph"
    shutil.copytree(
        _fixtures_root() / "typescript",
        project,
        ignore=shutil.ignore_patterns(".generated", ".codepotg"),
    )
    shutil.copy2(real_openapi_json_path, project / "openapi.json")
    config = project / "Codepotg.yml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            "input: ./openapi.yaml",
            "input: ./openapi.json",
        ),
        encoding="utf-8",
    )

    templates = project / "templates"
    shutil.rmtree(templates)
    templates.mkdir()
    (templates / "paths.yaml").write_text(
        """
selections:
  entities:
    select: entities
    as: entity
    scope: each
  frontends:
    select: frontends
    as: frontend
    scope: each

emissions:
  entity-contracts:
    selection: entities
    template: entity.ts.j2
    output: [entities, "[entity.name.path.o].ts"]
  frontend-contracts:
    selection: frontends
    template: frontend.ts.j2
    output: [frontends, "[frontend.name.path.o].ts"]
""".strip(),
        encoding="utf-8",
    )
    (templates / "entity.ts.j2").write_text(
        "{% set value = entity_contract.by_id[entity.name.raw.o] %}"
        "export const {{ entity.name.camel.o }}Store = \"{{ value.store }}\";\n"
        "export const {{ entity.name.camel.o }}PublicFields = {{ value.public_fields.count }};\n"
        "export const {{ entity.name.camel.o }}StorageFields = {{ value.storage_fields.count }};\n",
        encoding="utf-8",
    )
    (templates / "frontend.ts.j2").write_text(
        "{% set value = frontend_contract.by_id[frontend.name.raw.o] %}"
        "export const {{ frontend.name.camel.o }}Route = \"{{ value.route_prefix }}\";\n"
        "export const {{ frontend.name.camel.o }}Screens = {{ value.screens.count }};\n"
        "export const {{ frontend.name.camel.o }}Operations = {{ value.operations.count }};\n",
        encoding="utf-8",
    )

    result = GeneratorApp().generate(
        config_path=config,
        task_name="fixture",
    )

    output = project / ".generated"
    entity_file = output / "entities" / "app.ts"
    frontend_file = output / "frontends" / "admin.ts"
    written = set(result.tasks[0].written)

    assert entity_file in written
    assert frontend_file in written
    assert len(tuple((output / "entities").glob("*.ts"))) > 20
    assert len(tuple((output / "frontends").glob("*.ts"))) == 1

    entity_lines = entity_file.read_text(encoding="utf-8").splitlines()
    assert entity_lines[0] == 'export const appStore = "apps";'
    assert int(entity_lines[1].rsplit(" ", 1)[-1].rstrip(";")) > 0
    assert int(entity_lines[2].rsplit(" ", 1)[-1].rstrip(";")) > 0

    frontend_lines = frontend_file.read_text(encoding="utf-8").splitlines()
    assert frontend_lines[0] == 'export const adminRoute = "/admin";'
    assert int(frontend_lines[1].rsplit(" ", 1)[-1].rstrip(";")) > 0
    assert int(frontend_lines[2].rsplit(" ", 1)[-1].rstrip(";")) > 0


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"
