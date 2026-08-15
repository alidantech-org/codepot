from dryv.ir import (
    Contract,
    Event,
    Failure,
    Group,
    Name,
    Policy,
    Schema,
    SchemaKind,
    SemanticId,
    validate_contract,
)


def test_failure_is_group_owned_and_schema_reference_is_validated() -> None:
    schema = Schema(SemanticId("schema.problem"), Name("Problem"), SchemaKind.OBJECT)
    failure = Failure(SemanticId("failure.conflict"), Name("Conflict"), "CONFLICT", schema=schema.id)
    group = Group(SemanticId("group.test"), Name("test"), schemas=(schema,), failures=(failure,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (group,))
    assert not validate_contract(contract).has_errors


def test_policy_can_compose_policy_and_use_typed_context_schema() -> None:
    context = Schema(SemanticId("schema.auth-context"), Name("AuthContext"), SchemaKind.OBJECT)
    authenticated = Policy(SemanticId("policy.authenticated"), Name("Authenticated"), context_schema=context.id)
    admin = Policy(SemanticId("policy.admin"), Name("Admin"), roles=("admin",), policies=(authenticated.id,))
    event = Event(SemanticId("event.admin-action"), Name("AdminAction"), context_schema=context.id, policies=(admin.id,))
    group = Group(SemanticId("group.test"), Name("test"), schemas=(context,), policies=(authenticated, admin), events=(event,))
    assert not validate_contract(Contract(SemanticId("contract.test"), Name("Test"), (group,))).has_errors


def test_policy_composition_cycle_is_diagnostic() -> None:
    first = Policy(SemanticId("policy.first"), Name("First"), policies=(SemanticId("policy.second"),))
    second = Policy(SemanticId("policy.second"), Name("Second"), policies=(first.id,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), policies=(first, second)),))
    assert any(item.code == "IR_POLICY_CYCLE" for item in validate_contract(contract).errors)


def test_missing_event_policy_is_diagnostic_and_event_has_no_reverse_usage_list() -> None:
    event = Event(SemanticId("event.created"), Name("Created"), policies=(SemanticId("policy.missing"),))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), events=(event,)),))
    diagnostics = validate_contract(contract)
    assert any(item.code == "IR_MISSING_POLICY" for item in diagnostics.errors)
    assert not hasattr(event, "emitters")


def test_policy_rejects_duplicate_roles() -> None:
    try:
        Policy(SemanticId("policy.admin"), Name("Admin"), roles=("admin", "admin"))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate roles must be rejected")
