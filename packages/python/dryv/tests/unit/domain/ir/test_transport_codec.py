from dryv.ir import (
    Contract,
    Group,
    KernelData,
    Name,
    Operation,
    OperationOutput,
    Presentation,
    PresentationChannel,
    PresentationEntry,
    Schema,
    SchemaField,
    SchemaKind,
    SemanticId,
    TagSet,
    TypeExpression,
    ValueSource,
    View,
    contract_from_json,
    contract_from_yaml,
    contract_to_json,
    contract_to_yaml,
)


def _contract() -> Contract:
    company_id = SchemaField(
        id=SemanticId("company.field.id"),
        name=Name("id"),
        type=TypeExpression.primitive("string"),
        required=True,
    )
    company = Schema(
        id=SemanticId("company.schema"),
        name=Name("Company"),
        kind=SchemaKind.OBJECT,
        fields=(company_id,),
    )
    operation = Operation(
        id=SemanticId("company.list"),
        name=Name("listCompanies"),
        outputs=(
            OperationOutput(
                name=Name("items"),
                schema=company.id,
            ),
        ),
    )
    view = View(
        id=SemanticId("company.view"),
        name=Name("Companies"),
        schema=company.id,
        data=KernelData(tags=TagSet(("ui:data-table",))),
    )
    source = ValueSource(
        id=SemanticId("company.source"),
        name=Name("CompanyChoices"),
        operation=operation.id,
        output="items",
        value_field=company_id.id,
        label_fields=(company_id.id,),
    )
    group = Group(
        id=SemanticId("company.group"),
        name=Name("Companies"),
        schemas=(company,),
        operations=(operation,),
        views=(view,),
        value_sources=(source,),
    )
    presentation = Presentation(
        id=SemanticId("admin.presentation"),
        name=Name("Admin"),
        channel=PresentationChannel.WEB,
        entries=(
            PresentationEntry(
                id=SemanticId("admin.companies"),
                name=Name("Companies"),
                view=view.id,
                address="/companies",
            ),
        ),
    )
    return Contract(
        id=SemanticId("example.contract"),
        name=Name("Example"),
        groups=(group,),
        presentations=(presentation,),
    )


def test_canonical_json_round_trip_is_exact_and_deterministic() -> None:
    contract = _contract()
    first = contract_to_json(contract, pretty=False)
    second = contract_to_json(contract, pretty=False)
    assert first == second
    assert contract_from_json(first) == contract


def test_yaml_round_trip_preserves_tags_sources_and_presentations() -> None:
    contract = _contract()
    encoded = contract_to_yaml(contract)
    decoded = contract_from_yaml(encoded)
    assert decoded == contract
    assert decoded.groups[0].views[0].data.tags.has("ui:data-table")
    assert decoded.presentations[0].entries[0].address == "/companies"
