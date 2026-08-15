from dryv.ir import (
    AccessFacet,
    Contract,
    Event,
    Group,
    Name,
    Operation,
    OperationOutput,
    Policy,
    Schema,
    SchemaField,
    SchemaKind,
    SchemaUse,
    SemanticId,
    StorageCheck,
    StorageFieldMapping,
    StorageIndex,
    StorageMapping,
    StorageOnlyField,
    StorageReferenceMapping,
    StorageUniqueConstraint,
    TypeExpression,
    ValueSource,
    ValueSourceDependency,
    View,
    ViewConnection,
    ViewEventReaction,
    ViewTrigger,
    ViewWorkflowTrigger,
    Workflow,
    validate_contract,
)


def _field(value: str, name: str) -> SchemaField:
    return SchemaField(SemanticId(value), Name(name), TypeExpression.primitive("string"))


def test_storage_only_generated_fields_and_constraints_do_not_pollute_schema() -> None:
    semantic_id = _field("field.id", "id")
    schema = Schema(SemanticId("schema.item"), Name("Item"), SchemaKind.OBJECT, fields=(semantic_id,))
    mapping = StorageMapping(
        SemanticId("storage.item"),
        Name("ItemStorage"),
        schema.id,
        "items",
        fields=(StorageFieldMapping(semantic_id.id, "id", unique=True),),
        primary_key=(semantic_id.id,),
        storage_fields=(StorageOnlyField("created_at", "created_at", "timestamp", generated=True, computed="storage clock"),),
        unique_constraints=(StorageUniqueConstraint("uq_item_id", ("id",)),),
        storage_indexes=(StorageIndex("ix_created", ("created_at",)),),
        checks=(StorageCheck("ck_id", "id is present"),),
        version_field=semantic_id.id,
    )
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), schemas=(schema,), storage_mappings=(mapping,)),))
    assert not validate_contract(contract).has_errors
    assert tuple(item.name.raw.original for item in schema.fields) == ("id",)
    assert mapping.storage_fields[0].name == "created_at"


def test_storage_reference_mapping_validates_target_mapping_and_field() -> None:
    parent_id = _field("field.parent.id", "id")
    child_parent = _field("field.child.parent", "parentId")
    parent = Schema(SemanticId("schema.parent"), Name("Parent"), SchemaKind.OBJECT, fields=(parent_id,))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(child_parent,))
    parent_mapping = StorageMapping(SemanticId("storage.parent"), Name("ParentStorage"), parent.id, "parents", fields=(StorageFieldMapping(parent_id.id, "id"),))
    child_mapping = StorageMapping(SemanticId("storage.child"), Name("ChildStorage"), child.id, "children", fields=(StorageFieldMapping(child_parent.id, "parent_id"),), references=(StorageReferenceMapping(child_parent.id, parent_mapping.id, parent_id.id, "cascade"),))
    group = Group(SemanticId("group.test"), Name("test"), schemas=(parent, child), storage_mappings=(parent_mapping, child_mapping))
    assert not validate_contract(Contract(SemanticId("contract.test"), Name("Test"), (group,))).has_errors


def test_value_source_dependencies_are_neutral_and_cycle_checked() -> None:
    item_id = _field("field.item.id", "id")
    schema = Schema(SemanticId("schema.item"), Name("Item"), SchemaKind.OBJECT, fields=(item_id,))
    operation = Operation(SemanticId("operation.list"), Name("List"), inputs=(SchemaUse(Name("parent"), schema.id, required=False),), outputs=(OperationOutput(Name("items"), schema.id),))
    parent = ValueSource(SemanticId("source.parent"), Name("Parent"), operation.id, "items", item_id.id, (item_id.id,))
    child = ValueSource(SemanticId("source.child"), Name("Child"), operation.id, "items", item_id.id, (item_id.id,), dependencies=(ValueSourceDependency("parent", parent.id),))
    group = Group(SemanticId("group.test"), Name("test"), schemas=(schema,), operations=(operation,), value_sources=(parent, child))
    assert not validate_contract(Contract(SemanticId("contract.test"), Name("Test"), (group,))).has_errors

    first = ValueSource(SemanticId("source.first"), Name("First"), operation.id, "items", item_id.id, (item_id.id,), dependencies=(ValueSourceDependency("parent", SemanticId("source.second")),))
    second = ValueSource(SemanticId("source.second"), Name("Second"), operation.id, "items", item_id.id, (item_id.id,), dependencies=(ValueSourceDependency("parent", first.id),))
    cycle_group = Group(SemanticId("group.cycle"), Name("cycle"), schemas=(schema,), operations=(operation,), value_sources=(first, second))
    assert any(item.code == "IR_VALUE_SOURCE_CYCLE" for item in validate_contract(Contract(SemanticId("contract.cycle"), Name("Cycle"), (cycle_group,))).errors)


def test_view_composes_neutral_schema_operation_workflow_event_policy_source_and_view_relationships() -> None:
    item_id = _field("field.item.id", "id")
    schema = Schema(SemanticId("schema.item"), Name("Item"), SchemaKind.OBJECT, fields=(item_id,))
    policy = Policy(SemanticId("policy.view"), Name("ViewPolicy"))
    operation = Operation(SemanticId("operation.select"), Name("Select"), outputs=(OperationOutput(Name("items"), schema.id),))
    workflow = Workflow(SemanticId("workflow.open"), Name("Open"))
    event = Event(SemanticId("event.changed"), Name("Changed"))
    source = ValueSource(SemanticId("source.items"), Name("Items"), operation.id, "items", item_id.id, (item_id.id,))
    detail = View(SemanticId("view.detail"), Name("Detail"), schema=schema.id)
    main = View(
        SemanticId("view.main"),
        Name("Main"),
        schema=schema.id,
        triggers=(ViewTrigger(Name("select"), operation.id, "select"),),
        access=AccessFacet(policies=(policy.id,)),
        schemas=(schema.id,),
        fields=(item_id.id,),
        value_sources=(source.id,),
        workflow_triggers=(ViewWorkflowTrigger(Name("open"), workflow.id, "open"),),
        event_reactions=(ViewEventReaction(Name("refresh"), event.id, "refresh"),),
        connections=(ViewConnection(Name("detail"), detail.id),),
    )
    group = Group(SemanticId("group.test"), Name("test"), schemas=(schema,), policies=(policy,), operations=(operation,), workflows=(workflow,), events=(event,), value_sources=(source,), views=(main, detail))
    assert not validate_contract(Contract(SemanticId("contract.test"), Name("Test"), (group,))).has_errors


def test_invalid_storage_column_and_view_cross_reference_are_diagnostics() -> None:
    field = _field("field.id", "id")
    schema = Schema(SemanticId("schema.item"), Name("Item"), SchemaKind.OBJECT, fields=(field,))
    mapping = StorageMapping(SemanticId("storage.item"), Name("Storage"), schema.id, "items", fields=(StorageFieldMapping(field.id, "id"),), storage_indexes=(StorageIndex("ix_missing", ("missing",)),))
    view = View(SemanticId("view.item"), Name("View"), connections=(ViewConnection(Name("missing"), SemanticId("view.missing")),))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), schemas=(schema,), storage_mappings=(mapping,), views=(view,)),))
    codes = {item.code for item in validate_contract(contract).errors}
    assert "IR_MISSING_STORAGE_COLUMN" in codes
    assert "IR_MISSING_VIEW" in codes
