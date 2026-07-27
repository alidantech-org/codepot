from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from codepotg.domain.ir import (
    Contract,
    Event,
    Group,
    Operation,
    Policy,
    Presentation,
    PresentationEntry,
    Schema,
    SchemaKind,
    StorageMapping,
    ValueSource,
    View,
    Workflow,
    walk_groups,
)


class SelectionCardinality(StrEnum):
    EACH = "each"
    ALL = "all"


@dataclass(frozen=True, slots=True)
class SelectorDescriptor:
    id: str
    selected_kind: str
    cardinality: SelectionCardinality
    description: str


@dataclass(frozen=True, slots=True)
class SelectionContext:
    contract: Contract
    group: Group | None = None
    schema: Schema | None = None
    operation: Operation | None = None
    view: View | None = None
    storage_mapping: StorageMapping | None = None
    workflow: Workflow | None = None
    policy: Policy | None = None
    event: Event | None = None
    value_source: ValueSource | None = None
    presentation: Presentation | None = None
    presentation_entry: PresentationEntry | None = None

    @property
    def selected(self) -> object:
        candidates = (
            self.schema,
            self.operation,
            self.view,
            self.storage_mapping,
            self.workflow,
            self.policy,
            self.event,
            self.value_source,
            self.presentation_entry,
            self.presentation,
            self.group,
        )
        selected = tuple(value for value in candidates if value is not None)
        return selected[0] if selected else self.contract


class SelectorRegistry:
    def __init__(self, descriptors: tuple[SelectorDescriptor, ...]) -> None:
        ordered = tuple(sorted(descriptors, key=lambda item: item.id))
        ids = tuple(item.id for item in ordered)
        if len(ids) != len(set(ids)):
            raise ValueError("selector ids must be unique")
        self._descriptors = ordered

    @property
    def descriptors(self) -> tuple[SelectorDescriptor, ...]:
        return self._descriptors

    def describe(self, selector_id: str) -> SelectorDescriptor | None:
        return next((item for item in self._descriptors if item.id == selector_id), None)

    def select(self, selector_id: str, contract: Contract) -> tuple[SelectionContext, ...]:
        if self.describe(selector_id) is None:
            raise KeyError(f"unknown fixed selector: {selector_id}")

        groups = walk_groups(contract.groups)
        if selector_id in {"groups.each", "groups.all"}:
            return tuple(SelectionContext(contract=contract, group=group) for group in groups)
        if selector_id == "presentations.each":
            return tuple(
                SelectionContext(contract=contract, presentation=item)
                for item in contract.presentations
            )
        if selector_id == "presentations.entries.each":
            view_owners = _view_owners(groups)
            contexts: list[SelectionContext] = []
            for presentation in contract.presentations:
                for entry in presentation.entries:
                    contexts.append(
                        SelectionContext(
                            contract=contract,
                            group=view_owners.get(entry.view),
                            presentation=presentation,
                            presentation_entry=entry,
                        )
                    )
            return tuple(contexts)

        contexts: list[SelectionContext] = []
        for group in groups:
            contexts.extend(_select_from_group(selector_id, contract, group))
        return tuple(contexts)


def _view_owners(groups: tuple[Group, ...]) -> dict[object, Group]:
    owners: dict[object, Group] = {}
    for group in groups:
        for view in group.views:
            owners[view.id] = group
    return owners


def _select_from_group(
    selector_id: str,
    contract: Contract,
    group: Group,
) -> tuple[SelectionContext, ...]:
    if selector_id == "groups.schemas.each":
        return tuple(SelectionContext(contract, group, schema=item) for item in group.schemas)
    if selector_id == "groups.schemas.objects.each":
        return tuple(
            SelectionContext(contract, group, schema=item)
            for item in group.schemas
            if item.kind is SchemaKind.OBJECT
        )
    if selector_id == "groups.schemas.enums.each":
        return tuple(
            SelectionContext(contract, group, schema=item)
            for item in group.schemas
            if item.kind is SchemaKind.ENUM
        )
    if selector_id == "groups.operations.each":
        return tuple(SelectionContext(contract, group, operation=item) for item in group.operations)
    if selector_id == "groups.views.each":
        return tuple(SelectionContext(contract, group, view=item) for item in group.views)
    if selector_id == "groups.storage.mappings.each":
        return tuple(
            SelectionContext(contract, group, storage_mapping=item)
            for item in group.storage_mappings
        )
    if selector_id == "groups.workflows.each":
        return tuple(SelectionContext(contract, group, workflow=item) for item in group.workflows)
    if selector_id == "groups.policies.each":
        return tuple(SelectionContext(contract, group, policy=item) for item in group.policies)
    if selector_id == "groups.events.each":
        return tuple(SelectionContext(contract, group, event=item) for item in group.events)
    if selector_id == "groups.value_sources.each":
        return tuple(
            SelectionContext(contract, group, value_source=item)
            for item in group.value_sources
        )
    return ()


_DESCRIPTORS = (
    SelectorDescriptor(
        "groups.all",
        "group",
        SelectionCardinality.ALL,
        "All groups in deterministic outer-to-inner order.",
    ),
    SelectorDescriptor(
        "groups.each",
        "group",
        SelectionCardinality.EACH,
        "One invocation for each group.",
    ),
    SelectorDescriptor(
        "groups.events.each",
        "event",
        SelectionCardinality.EACH,
        "One invocation for each event declared under a group.",
    ),
    SelectorDescriptor(
        "groups.operations.each",
        "operation",
        SelectionCardinality.EACH,
        "One invocation for each operation declared under a group.",
    ),
    SelectorDescriptor(
        "groups.policies.each",
        "policy",
        SelectionCardinality.EACH,
        "One invocation for each policy declared under a group.",
    ),
    SelectorDescriptor(
        "groups.schemas.each",
        "schema",
        SelectionCardinality.EACH,
        "One invocation for each structural schema declared under a group.",
    ),
    SelectorDescriptor(
        "groups.schemas.enums.each",
        "schema",
        SelectionCardinality.EACH,
        "One invocation for each enum schema declared under a group.",
    ),
    SelectorDescriptor(
        "groups.schemas.objects.each",
        "schema",
        SelectionCardinality.EACH,
        "One invocation for each object schema declared under a group.",
    ),
    SelectorDescriptor(
        "groups.storage.mappings.each",
        "storage_mapping",
        SelectionCardinality.EACH,
        "One invocation for each storage mapping declared under a group.",
    ),
    SelectorDescriptor(
        "groups.value_sources.each",
        "value_source",
        SelectionCardinality.EACH,
        "One invocation for each selectable value source declared under a group.",
    ),
    SelectorDescriptor(
        "groups.views.each",
        "view",
        SelectionCardinality.EACH,
        "One invocation for each view declared under a group.",
    ),
    SelectorDescriptor(
        "groups.workflows.each",
        "workflow",
        SelectionCardinality.EACH,
        "One invocation for each workflow declared under a group.",
    ),
    SelectorDescriptor(
        "presentations.each",
        "presentation",
        SelectionCardinality.EACH,
        "One invocation for each contract-level presentation.",
    ),
    SelectorDescriptor(
        "presentations.entries.each",
        "presentation_entry",
        SelectionCardinality.EACH,
        "One invocation for each view placement in every presentation.",
    ),
)

DEFAULT_SELECTOR_REGISTRY = SelectorRegistry(_DESCRIPTORS)
