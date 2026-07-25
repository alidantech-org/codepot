from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp
from tests.fixtures.openapi import load_real_contract


def test_graph_templates_render_real_normalized_entity_and_frontend_roots(
    tmp_path: Path,
    real_openapi_yaml_path: Path,
) -> None:
    project = tmp_path / "normalized-graph"
    shutil.copytree(
        _fixtures_root() / "typescript",
        project,
        ignore=shutil.ignore_patterns(".generated", ".codepotg"),
    )
    shutil.copy2(real_openapi_yaml_path, project / "openapi.yaml")

    contract = load_real_contract(real_openapi_yaml_path)
    entity_contract = contract.meta["normalized_entities"]
    frontend_contract = contract.meta["normalized_frontends"]
    app_entity = entity_contract.entities.by_id["App"]
    admin_frontend = frontend_contract.by_id["admin"]

    assert app_entity.store == "apps"
    assert app_entity.resource is not None
    assert app_entity.resource.is_resolved
    assert app_entity.declared_fields.by_id["slug"].unique.value is True
    assert app_entity.declared_fields.by_id["status"].is_queryable
    assert admin_frontend.route_prefix == "/admin"
    assert "AppsTable" in admin_frontend.components.by_id
    assert "AppsListScreen" in admin_frontend.screens.by_id
    assert "findApps" in admin_frontend.operations.by_id

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
        config_path=project / "Codepotg.yml",
        task_name="fixture",
    )

    output = project / ".generated"
    entity_file = output / "entities" / "app.ts"
    frontend_file = output / "frontends" / "admin.ts"
    written = set(result.tasks[0].written)

    assert entity_file in written
    assert frontend_file in written
    assert len(written) == len(contract.entities) + frontend_contract.count
    assert entity_file.read_text(encoding="utf-8") == (
        'export const appStore = "apps";\n'
        f"export const appPublicFields = {app_entity.public_fields.count};\n"
        f"export const appStorageFields = {app_entity.storage_fields.count};\n"
    )
    assert frontend_file.read_text(encoding="utf-8") == (
        'export const adminRoute = "/admin";\n'
        f"export const adminScreens = {admin_frontend.screens.count};\n"
        f"export const adminOperations = {admin_frontend.operations.count};\n"
    )


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"
