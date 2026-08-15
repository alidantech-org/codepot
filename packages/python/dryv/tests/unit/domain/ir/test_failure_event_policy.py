from dryv.ir import Contract, Event, Failure, Group, Name, Policy, Schema, SchemaKind, SemanticId, validate_contract


def test_failure_is_group_owned_and_schema_reference_is_validated() -> None:
    schema = Schema(SemanticId("schema.problem"), Name("Problem"), SchemaKind.OBJECT)
    failure = Failure(SemanticId("failure.conflict"), Name("Conflict"), "CONFLICT", schema=schema.id)
    group = Group(SemanticId("group.test"), Name("test"), schemas=(schema,), failures=(failure,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (group,))
    assert not validate_contract(contract).has_errors


def test_event_has_no_authored_reverse_emitter_collection() -> None:
    event = Event(SemanticId("event.created"), Name("Created"))
    assert not hasattr(event, "emitters")


def test_policy_rejects_duplicate_roles() -> None:
    try:
        Policy(SemanticId("policy.admin"), Name("Admin"), roles=("admin", "admin"))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate roles must be rejected")
