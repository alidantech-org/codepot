from __future__ import annotations

from dryv.ir import (
    Contract,
    Group,
    Name,
    Operation,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    TypeExpression,
)
from dryv_template_jinja import JinjaTemplateEngine


def test_real_public_dryv_values_render_target_like_authored_text(render) -> None:
    identifier = TypeExpression.primitive("string")
    field = SchemaField(
        id=SemanticId("orders.Order.id"),
        name=Name("order id"),
        type=identifier,
        required=True,
    )
    schema = Schema(
        id=SemanticId("orders.Order"),
        name=Name("orders"),
        kind=SchemaKind.OBJECT,
        fields=(field,),
    )
    operation = Operation(id=SemanticId("orders.get"), name=Name("get order"))
    group = Group(
        id=SemanticId("orders"),
        name=Name("orders"),
        path=("orders",),
        schemas=(schema,),
        operations=(operation,),
    )
    contract = Contract(
        id=SemanticId("shop"),
        name=Name("shop API"),
        groups=(group,),
        version="1.0.0",
    )
    original_name_state = dict(vars(schema.name))
    template = (
        "contract={{ contract.name.kebab.s }}\n"
        "group={{ group.name.path.o }}\n"
        "schema={{ schema.name.pascal.s }}\n"
        "operation={{ operation.id.value }}\n"
        "field={{ field.name.camel.s }} required={{ field.required }}\n"
    )
    result = render(
        JinjaTemplateEngine(),
        template,
        context=(
            ("contract", contract),
            ("field", field),
            ("group", group),
            ("operation", operation),
            ("schema", schema),
        ),
    )
    assert result.content == (
        "contract=shop-api\n"
        "group=orders\n"
        "schema=Order\n"
        "operation=orders.get\n"
        "field=orderId required=True\n"
    )
    assert vars(schema.name) == original_name_state
