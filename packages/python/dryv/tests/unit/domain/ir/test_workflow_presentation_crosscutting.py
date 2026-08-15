from dryv.ir import Contract, Failure, Group, GuidanceKind, GuidanceNote, KernelData, Name, Presentation, PresentationChannel, PresentationEntry, SemanticId, TagSet, View, Workflow, validate_contract


def test_workflow_references_canonical_failure() -> None:
    failure = Failure(SemanticId("failure.workflow"), Name("WorkflowFailure"), "WORKFLOW_FAILED")
    workflow = Workflow(SemanticId("workflow.test"), Name("Workflow"), failures=(failure.id,))
    group = Group(SemanticId("group.test"), Name("test"), workflows=(workflow,), failures=(failure,))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (group,))
    assert not validate_contract(contract).has_errors


def test_presentation_navigation_cycle_is_diagnostic() -> None:
    view = View(SemanticId("view.test"), Name("View"))
    a_id = SemanticId("entry.a")
    b_id = SemanticId("entry.b")
    presentation = Presentation(SemanticId("presentation.test"), Name("Presentation"), PresentationChannel.WEB, entries=(PresentationEntry(a_id, Name("A"), view.id, navigation_parent=b_id), PresentationEntry(b_id, Name("B"), view.id, navigation_parent=a_id)))
    contract = Contract(SemanticId("contract.test"), Name("Test"), (Group(SemanticId("group.test"), Name("test"), views=(view,)),), presentations=(presentation,))
    assert any(item.code == "IR_PRESENTATION_NAVIGATION_CYCLE" for item in validate_contract(contract).errors)


def test_cross_cutting_tags_and_guidance_remain_shared_kernel_data() -> None:
    data = KernelData(tags=TagSet(("api", "security:reviewed")), guidance=(GuidanceNote(GuidanceKind.SECURITY, "Preserve authorization checks"),))
    assert data.tags.has("api")
    assert data.guidance[0].kind is GuidanceKind.SECURITY
