"""Strict-Jinja proof that optional selected-item contracts are safely empty."""

from __future__ import annotations

from pathlib import Path

from contracts.api import ApiEntity
from contracts.names import make_contract_name
from contracts.template import (
    TemplateEntity,
    TemplateFrontend,
    TemplateOperation,
    TemplateResource,
    TemplateSchema,
)
from emission.templates.renderer import render_template
from tests.fixtures.contracts import make_api_contract


def test_selected_contract_defaults_render_without_undefined_values(tmp_path: Path) -> None:
    api = make_api_contract()
    schema = TemplateSchema(api=api.schemas.all[0], name=api.schemas.all[0].name)
    operation = TemplateOperation(api=api.operations[0], name=api.operations[0].name)
    resource = TemplateResource(api=api.resources[0], name=api.resources[0].name)
    entity_api = ApiEntity(id="EmptyEntity", name=make_contract_name("EmptyEntity"))
    entity = TemplateEntity(api=entity_api, name=entity_api.name)
    frontend = TemplateFrontend(name=make_contract_name("emptyFrontend"))

    template_root = tmp_path / "templates"
    template_root.mkdir()
    template = template_root / "safe.txt.j2"
    template.write_text(
        "\n".join(
            (
                "schema_fields={{ schema.fields | length }}",
                "schema_description={{ schema.docs.description }}",
                "schema_dependencies={{ schema.emit.dependencies | length if schema.emit else 0 }}",
                "operation_parameters={{ operation.parameters | length }}",
                "operation_responses={{ operation.responses | length }}",
                "operation_request_missing={{ operation.request_body is none }}",
                "resource_operations={{ resource.operations | length }}",
                "resource_entities={{ resource.entities | length }}",
                "entity_fields={{ entity.fields | length }}",
                "entity_relations={{ entity.relations | length }}",
                "frontend_components={{ frontend.components | length }}",
                "frontend_screens={{ frontend.screens | length }}",
                "selected_frontend_missing={{ selected_frontend is none }}",
                "selected_frontends={{ selected_frontends | length }}",
                "file_missing={{ file is none }}",
            )
        ),
        encoding="utf-8",
    )

    output = render_template(
        template_root=template_root,
        relative_path=Path("safe.txt.j2"),
        context={
            "schema": schema,
            "operation": operation,
            "resource": resource,
            "entity": entity,
            "frontend": frontend,
            "selected_frontend": None,
            "selected_frontends": (),
            "file": None,
        },
    )

    assert "schema_fields=0" in output
    assert "schema_description=-" in output
    assert "schema_dependencies=0" in output
    assert "operation_parameters=0" in output
    assert "operation_responses=0" in output
    assert "operation_request_missing=True" in output
    assert "resource_operations=0" in output
    assert "resource_entities=0" in output
    assert "entity_fields=0" in output
    assert "entity_relations=0" in output
    assert "frontend_components=0" in output
    assert "frontend_screens=0" in output
    assert "selected_frontend_missing=True" in output
    assert "selected_frontends=0" in output
    assert "file_missing=True" in output
