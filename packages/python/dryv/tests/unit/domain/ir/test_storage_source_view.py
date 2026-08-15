from dryv.ir import Contract, Group, Name, Operation, OperationOutput, Schema, SchemaField, SchemaKind, SemanticId, StorageFieldMapping, StorageMapping, TypeExpression, ValueSource, View, ViewTrigger, validate_contract


def test_value_source_resolves_named_operation_output_and_fields() -> None:
    value = SchemaField(SemanticId("field.id"), Name("id"), TypeExpression.primitive("string"))
    label = SchemaField(SemanticId("field.label"), Name("label"), TypeExpression.primitive("string"))
    schema = Schema(SemanticId("schema.item"), Name("Item"), SchemaKind.OBJECT, fields=(value, label))
    operation = Operation(SemanticId("operation.list"), Name("List"), outputs=(OperationOutput(Name("items"), schema.id),))
    source = ValueSource(SemanticId("source.items"), Name("Items"), operation.id, "items", value.id, (label.id,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), schemas=(schema,), operations=(operation,), value_sources=(source,)),))
    assert not validate_contract(contract).has_errors


def test_storage_and_value_source_can_use_inherited_schema_fields() -> None:
    inherited = SchemaField(SemanticId("field.base.id"), Name("id"), TypeExpression.primitive("string"))
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(inherited,))
    label = SchemaField(SemanticId("field.child.label"), Name("label"), TypeExpression.primitive("string"))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(label,), extends=base.id)
    operation = Operation(SemanticId("operation.list"), Name("List"), outputs=(OperationOutput(Name("items"), child.id),))
    source = ValueSource(SemanticId("source.items"), Name("Items"), operation.id, "items", inherited.id, (label.id,))
    mapping = StorageMapping(SemanticId("storage.child"), Name("ChildStorage"), child.id, "children", fields=(StorageFieldMapping(inherited.id, "id"), StorageFieldMapping(label.id, "label")), primary_key=(inherited.id,))
    group = Group(SemanticId("group.test"), Name("test"), schemas=(base, child), operations=(operation,), storage_mappings=(mapping,), value_sources=(source,))
    assert not validate_contract(Contract(SemanticId("contract.test"), Name("Test"), (group,))).has_errors


def test_storage_rejects_duplicate_columns_and_view_rejects_duplicate_trigger_names() -> None:
    field_a = StorageFieldMapping(SemanticId("field.a"), "same")
    field_b = StorageFieldMapping(SemanticId("field.b"), "same")
    try:
        StorageMapping(SemanticId("storage.test"), Name("Storage"), SemanticId("schema.test"), "items", fields=(field_a, field_b))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate columns must fail")

    trigger = ViewTrigger(Name("Submit"), SemanticId("operation.submit"), "submit")
    try:
        View(SemanticId("view.test"), Name("View"), triggers=(trigger, trigger))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate trigger names must fail")
