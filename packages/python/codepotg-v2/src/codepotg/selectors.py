from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ir import (
    Contract,
    Event,
    Group,
    Operation,
    Policy,
    Schema,
    SchemaKind,
    StorageMapping,
    View,
    Workflow,
    walk_groups,
)


class SelectionCardinality(str, Enum):
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
    group: Group
    schema: Schema | None = None
    operation: Operation | None = None
    view: View | None = None
    storage_mapping: StorageMapping | None = None
    workflow: Workflow | None = None
    policy: Policy | None = None
    event: Event | None = None

    @property
    def selected(self) -> object:
        values = (
            self.schema,
            self.operation,
            self.view,
            self.storage_mapping,
            self.workflow,
            self.policy,
            self.event,
        )
        selected = tuple(value for value in values if value is not None)
        return selected[0] if selected else self.group


class SelectorRegistry:
    def __init__(self) -> None:
        self._descriptors = _DESCRIPTORS

    @property
    def descriptors(self) -> tuple[SelectorDescriptor, ...]:
        return self._descriptors

    def describe(self, selector_id: str) -> SelectorDescriptor | None:
        return next((item for item in self._descriptors if item.id == selector_id), None)

    def select(self, selector_id: str, contract: Contract) -> tuple[SelectionContext, ...]:
        if self.describe(selector_id) is None:
            raise KeyError(f"unknown fixed selector: {selector_id}")

        groups = walk_groups(contract.groups)
        contexts: list[SelectionContext] = []
        if selector_id in {"groups.each", "groups.all"}:
            return tuple(SelectionContext(contract=contract, group=group) for group in groups)

        for group in groups:
            if selector_id == "groups.schemas.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, schema=item)
                    for item in group.schemas
                )
            elif selector_id == "groups.schemas.objects.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, schema=item)
                    for item in group.schemas
                    if item.kind is SchemaKind.OBJECT
                )
            elif selector_id == "groups.schemas.enums.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, schema=item)
                    for item in group.schemas
                    if item.kind is SchemaKind.ENUM
                )
            elif selector_id == "groups.operations.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, operation=item)
                    for item in group.operations
                )
            elif selector_id == "groups.views.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, view=item)
                    for item in group.views
                )
            elif selector_id == "groups.storage.mappings.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, storage_mapping=item)
                    for item in group.storage_mappings
                )
            elif selector_id == "groups.workflows.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, workflow=item)
                    for item in group.workflows
                )
            elif selector_id == "groups.policies.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, policy=item)
                    for item in group.policies
                )
            elif selector_id == "groups.events.each":
                contexts.extend(
                    SelectionContext(contract=contract, group=group, event=item)
                    for item in group.events
                )
        return tuple(contexts)


_DESCRIPTORS = tuple(
    sorted(
        (
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
        ),
        key=lambda item: item.id,
    )
)

DEFAULT_SELECTOR_REGISTRY = SelectorRegistry()

__all__ = [
    "DEFAULT_SELECTOR_REGISTRY",
    "SelectionCardinality",
    "SelectionContext",
    "SelectorDescriptor",
    "SelectorRegistry",
]
