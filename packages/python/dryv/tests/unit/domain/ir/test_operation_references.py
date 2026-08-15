from dryv.ir import Contract, Event, EventEffect, Failure, Group, Name, Operation, OperationEffects, SemanticId, validate_contract


def test_operation_references_reusable_failure_and_event() -> None:
    failure = Failure(SemanticId("failure.conflict"), Name("Conflict"), "CONFLICT")
    event = Event(SemanticId("event.created"), Name("Created"))
    operation = Operation(SemanticId("operation.create"), Name("Create"), failures=(failure.id,), effects=OperationEffects(events=(EventEffect(event.id),)))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), operations=(operation,), failures=(failure,), events=(event,)),))
    assert not validate_contract(contract).has_errors


def test_missing_failure_reference_is_diagnostic() -> None:
    operation = Operation(SemanticId("operation.create"), Name("Create"), failures=(SemanticId("failure.missing"),))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), operations=(operation,)),))
    assert any(item.code == "IR_MISSING_FAILURE" for item in validate_contract(contract).errors)
