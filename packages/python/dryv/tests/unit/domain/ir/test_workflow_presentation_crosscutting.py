from dryv.ir import (
    Contract,
    Event,
    Failure,
    Group,
    GuidanceKind,
    GuidanceNote,
    KernelData,
    Name,
    Operation,
    Policy,
    Presentation,
    PresentationChannel,
    PresentationEntry,
    SemanticId,
    TagSet,
    View,
    Workflow,
    WorkflowStep,
    WorkflowStepKind,
    validate_contract,
)


def test_workflow_references_canonical_failure() -> None:
    failure = Failure(
        SemanticId("failure.workflow"),
        Name("WorkflowFailure"),
        "WORKFLOW_FAILED",
    )
    workflow = Workflow(
        SemanticId("workflow.test"),
        Name("Workflow"),
        failures=(failure.id,),
    )
    group = Group(
        SemanticId("group.test"),
        Name("test"),
        failures=(failure,),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (group,),
        workflows=(workflow,),
    )
    assert not validate_contract(contract).has_errors


def test_workflow_can_compose_child_workflow_and_cycles_are_rejected() -> None:
    child = Workflow(SemanticId("workflow.child"), Name("Child"))
    parent = Workflow(
        SemanticId("workflow.parent"),
        Name("Parent"),
        steps=(
            WorkflowStep(
                "child",
                WorkflowStepKind.WORKFLOW,
                workflow=child.id,
            ),
        ),
    )
    group = Group(SemanticId("group.test"), Name("test"))
    valid = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (group,),
        workflows=(parent, child),
    )
    assert not validate_contract(valid).has_errors

    first = Workflow(
        SemanticId("workflow.first"),
        Name("First"),
        steps=(
            WorkflowStep(
                "second",
                WorkflowStepKind.WORKFLOW,
                workflow=SemanticId("workflow.second"),
            ),
        ),
    )
    second = Workflow(
        SemanticId("workflow.second"),
        Name("Second"),
        steps=(
            WorkflowStep(
                "first",
                WorkflowStepKind.WORKFLOW,
                workflow=first.id,
            ),
        ),
    )
    cycle = Contract(
        SemanticId("contract.cycle"),
        Name("Cycle"),
        (Group(SemanticId("group.cycle"), Name("cycle")),),
        workflows=(first, second),
    )
    assert any(
        item.code == "IR_WORKFLOW_CYCLE"
        for item in validate_contract(cycle).errors
    )


def test_presentation_navigation_cycle_is_diagnostic() -> None:
    view = View(SemanticId("view.test"), Name("View"))
    a_id = SemanticId("entry.a")
    b_id = SemanticId("entry.b")
    presentation = Presentation(
        SemanticId("presentation.test"),
        Name("Presentation"),
        PresentationChannel.WEB,
        entries=(
            PresentationEntry(
                a_id,
                Name("A"),
                view.id,
                navigation_parent=b_id,
            ),
            PresentationEntry(
                b_id,
                Name("B"),
                view.id,
                navigation_parent=a_id,
            ),
        ),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (Group(SemanticId("group.test"), Name("test"), views=(view,)),),
        presentations=(presentation,),
    )
    assert any(
        item.code == "IR_PRESENTATION_NAVIGATION_CYCLE"
        for item in validate_contract(contract).errors
    )


def test_presentation_can_reference_related_behavior() -> None:
    view = View(SemanticId("view.test"), Name("View"))
    policy = Policy(SemanticId("policy.test"), Name("Policy"))
    operation = Operation(SemanticId("operation.test"), Name("Operation"))
    event = Event(SemanticId("event.test"), Name("Event"))
    workflow = Workflow(SemanticId("workflow.test"), Name("Workflow"))
    entry = PresentationEntry(
        SemanticId("entry.test"),
        Name("Entry"),
        view.id,
        policies=(policy.id,),
        operations=(operation.id,),
        events=(event.id,),
        workflows=(workflow.id,),
    )
    presentation = Presentation(
        SemanticId("presentation.test"),
        Name("Presentation"),
        PresentationChannel.WEB,
        entries=(entry,),
    )
    group = Group(
        SemanticId("group.test"),
        Name("test"),
        views=(view,),
        policies=(policy,),
        operations=(operation,),
        events=(event,),
    )
    contract = Contract(
        SemanticId("contract.test"),
        Name("Test"),
        (group,),
        presentations=(presentation,),
        workflows=(workflow,),
    )
    assert not validate_contract(contract).has_errors


def test_cross_cutting_tags_and_guidance_remain_shared_kernel_data() -> None:
    data = KernelData(
        tags=TagSet(("api", "security:reviewed")),
        guidance=(
            GuidanceNote(
                GuidanceKind.SECURITY,
                "Preserve authorization checks",
            ),
        ),
    )
    assert data.tags.has("api")
    assert data.guidance[0].kind is GuidanceKind.SECURITY
