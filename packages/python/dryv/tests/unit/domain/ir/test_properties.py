from dryv.ir import Contract, Group, Name, Property, Schema, SchemaField, SchemaKind, SemanticId, TypeExpression, validate_contract


def test_group_owned_property_can_be_referenced_by_schema_field() -> None:
    prop = Property(SemanticId("prop.email"), Name("email"), TypeExpression.primitive("string"))
    field = SchemaField(SemanticId("field.email"), Name("email"), TypeExpression.primitive("string"), property=prop.id)
    schema = Schema(SemanticId("schema.user"), Name("User"), SchemaKind.OBJECT, fields=(field,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), properties=(prop,), schemas=(schema,)),))
    assert not validate_contract(contract).has_errors


def test_missing_property_reference_is_diagnostic() -> None:
    field = SchemaField(SemanticId("field.email"), Name("email"), TypeExpression.primitive("string"), property=SemanticId("prop.missing"))
    schema = Schema(SemanticId("schema.user"), Name("User"), SchemaKind.OBJECT, fields=(field,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), schemas=(schema,)),))
    diagnostics = validate_contract(contract)
    assert any(item.code == "IR_MISSING_PROPERTY" for item in diagnostics.errors)
