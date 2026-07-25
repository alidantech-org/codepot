from __future__ import annotations

import shutil
from pathlib import Path

from app import GeneratorApp
from tests.fixtures.openapi import load_real_contract


def test_real_typescript_project_generates_explicit_graph_incrementally(
    tmp_path: Path,
    real_openapi_yaml_path: Path,
) -> None:
    project = tmp_path / "typescript-graph"
    shutil.copytree(
        _fixtures_root() / "typescript",
        project,
        ignore=shutil.ignore_patterns(".generated", ".codepotg"),
    )
    shutil.copy2(real_openapi_yaml_path, project / "openapi.yaml")
    contract = load_real_contract(real_openapi_yaml_path)

    templates = project / "templates"
    shutil.rmtree(templates)
    templates.mkdir()
    (templates / "paths.yaml").write_text(
        """
template_extension: .j2
imports:
  strategy: relative

selections:
  schemas:
    select: schemas.all
    as: schema
    scope: each
  enums:
    select: schemas.emit_enums
    as: enum
    scope: each
  resources:
    select: resources
    as: resource
    scope: each

emissions:
  schema-types:
    selection: schemas
    template: schema.ts.j2
    output: [types, "[schema.name.path.o].ts"]
    provides: [schemas]
    imports:
      schemas: schema-types
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
    imports:
      schemas: schema-types

barrels:
  enum-barrel:
    template: index.ts.j2
    output: [models, index.ts]
    exports: [enum-types]
    scope: all
""".strip(),
        encoding="utf-8",
    )
    (templates / "schema.ts.j2").write_text(
        "export type {{ schema.name.pascal.o }}Contract = unknown;\n",
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
        "schema={{ schema_contract.by_id[enum.api.id].id }}\n",
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
    schema_count = len(contract.schemas.all)
    enum_count = len(contract.schemas.emit_enums)
    resource_count = len(contract.resources)
    expected_count = schema_count + (enum_count * 2) + resource_count + 1

    assert len(task.written) == expected_count
    assert task.updated == []
    assert task.unchanged == []
    assert all(path.is_file() for path in task.written)
    assert (project / ".codepotg" / "cache" / "openapi" / "manifest.json").is_file()

    assert (output / "types" / "app.ts").is_file()
    assert (output / "types" / "app_list_query.ts").is_file()

    enum_type = (output / "models" / "app_status.ts").read_text(
        encoding="utf-8"
    )
    assert "appStatusEnum" in enum_type
    assert 'appStatusEnum = "enum"' in enum_type
    assert "active,suspended,disabled" in enum_type

    metadata = (output / "metadata" / "app_status.txt").read_text(
        encoding="utf-8"
    )
    assert "selection=enums" in metadata
    assert "schema=AppStatus" in metadata

    resource = (output / "resources" / "apps.ts").read_text(encoding="utf-8")
    assert 'appsRoute = "/platform/apps"' in resource

    barrel = (output / "models" / "index.ts").read_text(encoding="utf-8")
    assert "models/app_status.ts" in barrel
    assert "models/shared_sort.ts" in barrel

    written_messages = [
        event.message.replace("\\", "/")
        for event in events
        if event.stage in {"file_written", "file_unchanged"}
    ]
    schema_index = next(
        index
        for index, message in enumerate(written_messages)
        if "types/app_list_query.ts" in message
    )
    resource_index = next(
        index
        for index, message in enumerate(written_messages)
        if "resources/apps.ts" in message
    )
    member_index = next(
        index
        for index, message in enumerate(written_messages)
        if "models/app_status.ts" in message
    )
    barrel_index = next(
        index
        for index, message in enumerate(written_messages)
        if "models/index.ts" in message
    )
    assert schema_index < resource_index
    assert member_index < barrel_index
    assert any(event.stage == "file_planned" for event in events)
    assert any(event.stage == "file_rendered" for event in events)
    assert any(event.stage == "emission_complete" for event in events)
    resolver_event = next(
        event for event in events if event.stage == "resolver_complete"
    )
    assert f"loaded {enum_count} record(s)" in resolver_event.message


def _fixtures_root() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "projects"
