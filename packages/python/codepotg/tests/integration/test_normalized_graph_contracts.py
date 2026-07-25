from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp


def test_graph_templates_render_normalized_entity_and_frontend_roots(
    tmp_path: Path,
) -> None:
    project = tmp_path / "normalized-graph"
    shutil.copytree(
        _fixtures_root() / "typescript",
        project,
        ignore=shutil.ignore_patterns(".generated", ".codepotg"),
    )
    (project / "openapi.yaml").write_text(
        """
openapi: 3.1.0
info:
  title: Normalized Graph API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: listUsers
      responses:
        "200":
          description: OK
components:
  schemas:
    UserModel:
      type: object
x-codegen:
  entities:
    UserEntity:
      store: users
      visibility: [backend, storage, api]
      fields:
        id:
          type: string
          readonly: true
        name:
          type: string
          editable: true
      backendFields:
        internalNote:
          type: string
  frontends:
    admin:
      title: Admin Console
      routePrefix: /admin
      components:
        user-table:
          props: '#/components/schemas/UserModel'
          uses:
            - alias: loadUsers
              operation: listUsers
      screens:
        users:
          route: /users
          components: [user-table]
          uses:
            - alias: loadUsers
              operation: listUsers
""".strip(),
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
        "{% set value = entity_contract.by_id[entity.api.id] %}"
        "export const {{ entity.name.camel.o }}Store = \"{{ value.store }}\";\n"
        "export const {{ entity.name.camel.o }}PublicFields = {{ value.public_fields.count }};\n"
        "export const {{ entity.name.camel.o }}StorageFields = {{ value.storage_fields.count }};\n",
        encoding="utf-8",
    )
    (templates / "frontend.ts.j2").write_text(
        "{% set value = frontend_contract.by_id[frontend.name.raw] %}"
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
    entity_file = output / "entities" / "user_entity.ts"
    frontend_file = output / "frontends" / "admin.ts"
    assert set(result.tasks[0].written) == {entity_file, frontend_file}
    assert entity_file.read_text(encoding="utf-8") == (
        'export const userEntityStore = "users";\n'
        "export const userEntityPublicFields = 2;\n"
        "export const userEntityStorageFields = 3;\n"
    )
    assert frontend_file.read_text(encoding="utf-8") == (
        'export const adminRoute = "/admin";\n'
        "export const adminScreens = 1;\n"
        "export const adminOperations = 1;\n"
    )


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"
