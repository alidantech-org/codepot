from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp


def test_real_typescript_project_generates_explicit_graph_incrementally(
    tmp_path: Path,
) -> None:
    project = tmp_path / "typescript-graph"
    shutil.copytree(
        _fixtures_root() / "typescript",
        project,
        ignore=shutil.ignore_patterns(".generated", ".codepotg"),
    )
    (project / "openapi.yaml").write_text(
        """
openapi: 3.1.0
info:
  title: Graph API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: listUsers
      x-codegen:
        resource:
          name: users
      responses:
        "200":
          description: OK
components:
  schemas:
    UserStatus:
      title: User status
      type: string
      minLength: 3
      enum: [active, inactive]
      x-codegen:
        kind: enum
x-codegen:
  resources:
    users:
      name: users
      route: /users
""".strip(),
        encoding="utf-8",
    )
    templates = project / "templates"
    shutil.rmtree(templates)
    templates.mkdir()
    (templates / "paths.yaml").write_text(
        """
template_extension: .j2
imports:
  strategy: relative

selections:
  enums:
    select: schemas.emit_enums
    as: enum
    scope: each
  resources:
    select: resources
    as: resource
    scope: each

emissions:
  enum-types:
    selection: enums
    template: enum.ts.j2
    output: [models, "[enum.name.path.o].ts"]
    provides: [enums]
  enum-metadata:
    selection: enums
    template: enum.meta.txt.j2
    output: [metadata, "[enum.name.path.o].txt"]
    provides: [metadata]
  resource-files:
    selection: resources
    template: resource.ts.j2
    output: [resources, "[resource.name.path.o].ts"]
    provides: [resources]

barrels:
  enum-barrel:
    template: index.ts.j2
    output: [models, index.ts]
    exports: [enum-types]
    scope: all
""".strip(),
        encoding="utf-8",
    )
    (templates / "enum.ts.j2").write_text(
        "export const {{ enum.name.camel.o }}Enum = \"{{ source.kind }}\";\n"
        "export const {{ enum.name.camel.o }}Values = "
        "\"{{ source.get('enum', ()) | join(',') }}\";\n",
        encoding="utf-8",
    )
    (templates / "enum.meta.txt.j2").write_text(
        "symbol={{ enum.lang.symbol_name }}\n"
        "selection={{ selection.name }}\n"
        "schemaTitle={{ schema_contract.by_id[enum.api.id].title.value }}\n"
        "minLength={{ schema_contract.by_id[enum.api.id].min_length.value }}\n",
        encoding="utf-8",
    )
    (templates / "resource.ts.j2").write_text(
        "export const {{ resource.name.camel.o }}Resource = \"{{ resource.api.id }}\";\n"
        "export const {{ resource.name.camel.o }}Route = "
        "\"{{ codegen_contract.resources.by_id[resource.api.id].route }}\";\n",
        encoding="utf-8",
    )
    (templates / "index.ts.j2").write_text(
        "{% for member in barrel.members %}{{ member.output_path }}\n{% endfor %}",
        encoding="utf-8",
    )

    events = []
    result = GeneratorApp().generate(
        config_path=project / "Codepotg.yml",
        task_name="fixture",
        progress=events.append,
    )

    task = result.tasks[0]
    output = project / ".generated"
    expected = {
        output / "models" / "user_status.ts",
        output / "metadata" / "user_status.txt",
        output / "resources" / "users.ts",
        output / "models" / "index.ts",
    }
    assert set(task.written) == expected
    assert task.updated == []
    assert task.unchanged == []
    assert all(path.is_file() for path in expected)
    assert (project / ".codepotg" / "cache" / "openapi" / "manifest.json").is_file()

    enum_type = (output / "models" / "user_status.ts").read_text(encoding="utf-8")
    assert "userStatusEnum" in enum_type
    assert 'userStatusEnum = "enum"' in enum_type
    assert "active,inactive" in enum_type
    metadata = (output / "metadata" / "user_status.txt").read_text(encoding="utf-8")
    assert "selection=enums" in metadata
    assert "schemaTitle=User status" in metadata
    assert "minLength=3" in metadata
    resource = (output / "resources" / "users.ts").read_text(encoding="utf-8")
    assert 'usersRoute = "/users"' in resource
    barrel = (output / "models" / "index.ts").read_text(encoding="utf-8")
    assert "models/user_status.ts" in barrel

    written_messages = [
        event.message.replace("\\", "/")
        for event in events
        if event.stage in {"file_written", "file_unchanged"}
    ]
    member_index = next(
        index for index, message in enumerate(written_messages) if "user_status.ts" in message
    )
    barrel_index = next(
        index for index, message in enumerate(written_messages) if "models/index.ts" in message
    )
    assert member_index < barrel_index
    assert any(event.stage == "file_planned" for event in events)
    assert any(event.stage == "file_rendered" for event in events)
    assert any(event.stage == "emission_complete" for event in events)
    resolver_event = next(event for event in events if event.stage == "resolver_complete")
    assert "loaded 1 record(s)" in resolver_event.message


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"
