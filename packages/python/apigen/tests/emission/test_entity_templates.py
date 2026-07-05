from __future__ import annotations

from pathlib import Path

from src.contracts.api import (
    ApiContract,
    ApiDocumentInfo,
    ApiEntity,
    ApiEntityField,
    ApiFieldKind,
    ApiFieldType,
    ApiResource,
    ApiSchema,
    ApiSchemaGroups,
    ApiSchemaKind,
)
from src.contracts.names import make_contract_name
from src.emission.engine import emit
from src.languages.typescript.adapter import TypeScriptLanguageAdapter


def test_paths_yaml_can_select_entities_and_render_template(tmp_path: Path) -> None:
    template_root = tmp_path / "templates"
    (template_root / "{entity}").mkdir(parents=True)
    (template_root / "paths.yaml").write_text(
        """
template_extension: ".j2"
strip_template_extension: true
folders:
  entity:
    select: entities
    as: entity
    parts:
      - gen
      - backend
      - [entity.resource.path]
      - [entity.resource.name.kebab.o]
      - entities
""".strip(),
        encoding="utf-8",
    )
    (template_root / "{entity}" / "[entity.meta.file_name].ts.j2").write_text(
        """
export class {{ entity.meta.class_name }} {
{% for field in entity.fields %}
  {{ field.lang.display_name }}!: {{ field.lang.type }};
{% endfor %}
}
""".strip(),
        encoding="utf-8",
    )

    contract = TypeScriptLanguageAdapter().build_template_contract(
        api=_api_contract(),
        output_path=tmp_path / "out",
        template_root=template_root,
        dry_run=False,
    )

    result = emit(contract)
    output = (
        tmp_path
        / "out"
        / "gen"
        / "backend"
        / "platform"
        / "apps"
        / "entities"
        / "app.entity.ts"
    )

    assert output in result.write_result.created
    assert "export class AppEntity" in output.read_text(encoding="utf-8")
    assert "name!: string;" in output.read_text(encoding="utf-8")


def _api_contract() -> ApiContract:
    app_ref = "#/components/schemas/App"
    return ApiContract(
        info=ApiDocumentInfo(title="Entity API", api_version="v1"),
        resources=(
            ApiResource(
                id="apps",
                name=make_contract_name("apps"),
                path=("platform",),
                operations_count=0,
            ),
        ),
        schemas=ApiSchemaGroups(
            all=(
                ApiSchema(
                    id="App",
                    name=make_contract_name("App"),
                    ref=app_ref,
                    kind=ApiSchemaKind.MODEL,
                    resource="apps",
                ),
            ),
        ),
        entities=(
            ApiEntity(
                id="apps.App",
                name=make_contract_name("App"),
                resource="apps",
                schema_ref=app_ref,
                fields=(
                    ApiEntityField(
                        id="name",
                        name=make_contract_name("name"),
                        type=ApiFieldType(kind=ApiFieldKind.PRIMITIVE, type="string"),
                    ),
                ),
            ),
        ),
    )
