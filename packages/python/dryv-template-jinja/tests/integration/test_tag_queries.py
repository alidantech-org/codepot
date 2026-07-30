from dryv.api import CancellationToken
from dryv.ir import KernelData, Name, Schema, SchemaKind, SemanticId, TagSet
from dryv.ports import RenderRequest
from dryv_template_jinja.plugin import create_plugin


def test_semantic_tags_are_available_as_safe_boolean_queries() -> None:
    schema = Schema(
        id=SemanticId("users.schema"),
        name=Name("User"),
        kind=SchemaKind.OBJECT,
        data=KernelData(
            tags=TagSet(
                (
                    "orm:prisma",
                    "orm:prisma:custom_sql",
                    "ui:admin",
                )
            )
        ),
    )
    result = create_plugin().render(
        RenderRequest(
            template_id="tag-test.ts.jinja",
            source=(
                '{% if schema.tags.has("orm:prisma:custom_sql") %}'
                "custom"
                "{% endif %}"
                '{% if schema.tags.has_all("orm:prisma", "ui:admin") %}'
                ":admin"
                "{% endif %}"
            ),
            context=(("schema", schema),),
        ),
        CancellationToken(),
    )
    assert not result.diagnostics.has_errors
    assert result.content == "custom:admin"
