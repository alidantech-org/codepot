from dryv.ir import (
    Contract,
    Event,
    EventEffect,
    EventsFacet,
    Group,
    Name,
    Operation,
    OperationEffects,
    OperationFacets,
    OperationOutput,
    OperationRelations,
    Policy,
    Schema,
    SchemaKind,
    SchemaUse,
    SemanticId,
    Workflow,
    validate_contract,
)


def test_operation_supports_semantic_absence_and_multiple_named_io() -> None:
    empty = Operation(SemanticId("operation.empty"), Name("Empty"))
    assert empty.inputs == () and empty.outputs == ()

    input_schema = Schema(
        SemanticId("schema.input"),
        Name("Input"),
        SchemaKind.OBJECT,
    )
    output_schema = Schema(
        SemanticId("schema.output"),
        Name("Output"),
        SchemaKind.OBJECT,
    )
    operation = Operation(
        SemanticId("operation.many"),
        Name("Many"),
        inputs=(
            SchemaUse(Name("left"), input_schema.id),
            SchemaUse(Name("right"), input_schema.id),
        ),
        outputs=(
            OperationOutput(Name("primary"), output_schema.id),
            OperationOutput(Name("secondary"), output_schema.id, optional=True),
        ),
    )
    assert tuple(item.name.raw.original for item in operation.inputs) == (
        "left",
        "right",
    )
    assert tuple(
        item.name.raw.original
        for item in operation.outputs
        if item.name is not None
    ) == ("primary", "secondary")


def test_operation_owns_subject_policy_event_and_composition_relationships() -> None:
    subject = Schema(
        SemanticId("schema.pool"),
        Name("Pool"),
        SchemaKind.OBJECT,
    )
    policy = Policy(SemanticId("policy.manage"), Name("Manage"))
    emitted = Event(SemanticId("event.created"), Name("Created"))
    consumed = Event(SemanticId("event.requested"), Name("Requested"))
    workflow = Workflow(SemanticId("workflow.followup"), Name("Followup"))
    dependency = Operation(SemanticId("operation.prepare"), Name("Prepare"))
    operation = Operation(
        SemanticId("operation.create"),
        Name("Create"),
        effects=OperationEffects(events=(EventEffect(emitted.id),)),
        facets=OperationFacets(events=EventsFacet(consumes=(consumed.id,))),
        subjects=(subject.id,),
        policies=(policy.id,),
        relations=OperationRelations(
            invokes=(dependency.id,),
            requires=(dependency.id,),
            after=(dependency.id,),
            triggers_workflows=(workflow.id,),
        ),
    )
    group = Group(
        SemanticId("group.test"),
        Name("test"),
        schemas=(subject,),
        policies=(policy,),
        events=(emitted, consumed),
        operations=(dependency, operation),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (group,),
        workflows=(workflow,),
    )
    assert not validate_contract(contract).has_errors


def test_missing_operation_relation_is_diagnostic() -> None:
    operation = Operation(
        SemanticId("operation.create"),
        Name("Create"),
        relations=OperationRelations(
            requires=(SemanticId("operation.missing"),),
        ),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (
            Group(
                SemanticId("group.test"),
                Name("test"),
                operations=(operation,),
            ),
        ),
    )
    assert any(
        item.code == "IR_MISSING_OPERATION"
        for item in validate_contract(contract).errors
    )


def test_operation_order_cycles_are_rejected_but_invocation_recursion_is_not_an_order_cycle() -> None:
    first_id = SemanticId("operation.first")
    second_id = SemanticId("operation.second")
    first = Operation(
        first_id,
        Name("First"),
        relations=OperationRelations(before=(second_id,), invokes=(first_id,)),
    )
    second = Operation(
        second_id,
        Name("Second"),
        relations=OperationRelations(before=(first_id,)),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (
            Group(
                SemanticId("group.test"),
                Name("test"),
                operations=(first, second),
            ),
        ),
    )
    diagnostics = validate_contract(contract)
    assert any(
        item.code == "IR_OPERATION_ORDER_CYCLE"
        for item in diagnostics.errors
    )
    assert not any(
        item.code == "IR_OPERATION_INVOCATION_CYCLE"
        for item in diagnostics.errors
    )
