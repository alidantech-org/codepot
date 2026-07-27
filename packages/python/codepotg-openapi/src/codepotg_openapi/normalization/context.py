from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codepotg.api import CancellationToken
from codepotg.ir import (
    Event,
    Group,
    GroupFacets,
    KernelData,
    Name,
    Operation,
    OperationEffects,
    OperationFacets,
    OperationFailure,
    OperationOutput,
    Policy,
    Schema,
    SchemaUse,
    SemanticId,
    StorageMapping,
    View,
    Workflow,
)

from ..diagnostics import DiagnosticBag
from ..options import OpenApiOptions
from ..parsing.document import ParsedDocument
from ..references.resolver import ReferenceResolver
from .identities import IdentityRegistry, stable_id
from .provenance import kernel_data


@dataclass(slots=True)
class OperationBuilder:
    id: SemanticId
    name: Name
    inputs: list[SchemaUse] = field(default_factory=list)
    outputs: list[OperationOutput] = field(default_factory=list)
    failures: list[OperationFailure] = field(default_factory=list)
    effects: OperationEffects = field(default_factory=OperationEffects)
    facets: OperationFacets = field(default_factory=OperationFacets)
    data: KernelData = field(default_factory=KernelData)

    def freeze(self) -> Operation:
        return Operation(
            id=self.id,
            name=self.name,
            inputs=tuple(self.inputs),
            outputs=tuple(self.outputs),
            failures=tuple(self.failures),
            effects=self.effects,
            facets=self.facets,
            data=self.data,
        )


@dataclass(slots=True)
class GroupBuilder:
    id: SemanticId
    name: Name
    path: tuple[str, ...]
    data: KernelData
    schemas: dict[SemanticId, Schema] = field(default_factory=dict)
    operations: dict[SemanticId, OperationBuilder] = field(default_factory=dict)
    views: dict[SemanticId, View] = field(default_factory=dict)
    storage_mappings: dict[SemanticId, StorageMapping] = field(default_factory=dict)
    workflows: dict[SemanticId, Workflow] = field(default_factory=dict)
    policies: dict[SemanticId, Policy] = field(default_factory=dict)
    events: dict[SemanticId, Event] = field(default_factory=dict)
    facets: GroupFacets = field(default_factory=GroupFacets)

    def freeze(self) -> Group:
        return Group(
            id=self.id,
            name=self.name,
            path=self.path,
            schemas=tuple(sorted(self.schemas.values(), key=lambda item: item.id.value)),
            operations=tuple(
                item.freeze()
                for item in sorted(self.operations.values(), key=lambda item: item.id.value)
            ),
            views=tuple(sorted(self.views.values(), key=lambda item: item.id.value)),
            storage_mappings=tuple(
                sorted(self.storage_mappings.values(), key=lambda item: item.id.value)
            ),
            workflows=tuple(sorted(self.workflows.values(), key=lambda item: item.id.value)),
            policies=tuple(sorted(self.policies.values(), key=lambda item: item.id.value)),
            events=tuple(sorted(self.events.values(), key=lambda item: item.id.value)),
            facets=self.facets,
            data=self.data,
        )


@dataclass(slots=True)
class NormalizationContext:
    root: ParsedDocument
    resolver: ReferenceResolver
    options: OpenApiOptions
    diagnostics: DiagnosticBag
    cancellation: CancellationToken
    # Reserved for the future OA-010 typed decoder. Runtime code passes None
    # until that decoder exists; no missing private module is imported.
    x_codegen: Any | None = None
    identities: IdentityRegistry = field(default_factory=IdentityRegistry)
    groups: dict[str, GroupBuilder] = field(default_factory=dict)
    schema_by_ref: dict[tuple[str, str], SemanticId] = field(default_factory=dict)
    schema_by_name: dict[str, SemanticId] = field(default_factory=dict)
    schema_owner: dict[SemanticId, str] = field(default_factory=dict)
    field_by_name: dict[tuple[SemanticId, str], SemanticId] = field(default_factory=dict)
    operation_by_key: dict[str, SemanticId] = field(default_factory=dict)
    operation_owner: dict[SemanticId, str] = field(default_factory=dict)
    policy_by_name: dict[str, SemanticId] = field(default_factory=dict)
    event_by_name: dict[str, SemanticId] = field(default_factory=dict)
    view_by_name: dict[str, SemanticId] = field(default_factory=dict)

    @property
    def source_key(self) -> str:
        return self.root.source.logical_id

    def ensure_group(
        self,
        name: str,
        *,
        pointer: str = "",
        explicit_id: str | None = None,
        document: ParsedDocument | None = None,
    ) -> GroupBuilder:
        existing = self.groups.get(name)
        if existing is not None:
            return existing
        doc = document or self.root
        semantic_id = stable_id(
            source=doc.source.logical_id,
            category="group",
            pointer=pointer or f"group:{name}",
            hint=name,
            explicit=explicit_id,
        )
        self._register(semantic_id, pointer or f"group:{name}", doc)
        projected_name = Name(name)
        builder = GroupBuilder(
            id=semantic_id,
            name=projected_name,
            path=(
                projected_name.kebab.original
                if hasattr(projected_name, "kebab")
                else _path_name(name),
            ),
            data=kernel_data(
                doc,
                pointer,
                options=self.options,
                diagnostics=self.diagnostics,
            ),
        )
        self.groups[name] = builder
        return builder

    def add_schema(
        self,
        group: str,
        schema: Schema,
        document: ParsedDocument,
        pointer: str,
    ) -> None:
        self._register(schema.id, pointer, document)
        self.ensure_group(group, document=document).schemas[schema.id] = schema
        self.schema_owner[schema.id] = group

    def add_operation(
        self,
        group: str,
        operation: OperationBuilder,
        document: ParsedDocument,
        pointer: str,
        keys: tuple[str, ...],
    ) -> None:
        self._register(operation.id, pointer, document)
        self.ensure_group(group, document=document).operations[operation.id] = operation
        self.operation_owner[operation.id] = group
        self.operation_by_key[operation.id.value] = operation.id
        for key in keys:
            previous = self.operation_by_key.get(key)
            if previous is not None and previous != operation.id:
                self.diagnostics.error(
                    "OA_OPERATION_DUPLICATE_KEY",
                    f"operation lookup key {key!r} is ambiguous",
                    span=document.span(pointer),
                )
            else:
                self.operation_by_key[key] = operation.id

    def operation(self, reference: str) -> OperationBuilder | None:
        operation_id = self.operation_by_key.get(reference)
        if operation_id is None:
            return None
        owner = self.operation_owner[operation_id]
        return self.groups[owner].operations[operation_id]

    def schema(self, reference: str) -> SemanticId | None:
        if reference in self.schema_by_name:
            return self.schema_by_name[reference]
        try:
            candidate = SemanticId(reference)
        except ValueError:
            return None
        return candidate if candidate in self.schema_owner else None

    def policy(self, reference: str) -> SemanticId | None:
        if reference in self.policy_by_name:
            return self.policy_by_name[reference]
        try:
            candidate = SemanticId(reference)
        except ValueError:
            return None
        return (
            candidate
            if any(candidate in group.policies for group in self.groups.values())
            else None
        )

    def event(self, reference: str) -> SemanticId | None:
        if reference in self.event_by_name:
            return self.event_by_name[reference]
        try:
            candidate = SemanticId(reference)
        except ValueError:
            return None
        return (
            candidate
            if any(candidate in group.events for group in self.groups.values())
            else None
        )

    def freeze_groups(self) -> tuple[Group, ...]:
        return tuple(
            group.freeze()
            for group in sorted(self.groups.values(), key=lambda item: item.id.value)
        )

    def _register(
        self,
        semantic_id: SemanticId,
        pointer: str,
        document: ParsedDocument,
    ) -> None:
        previous = self.identities.register(
            semantic_id,
            f"{document.source.logical_id}#{pointer}",
        )
        if previous is not None:
            self.diagnostics.error(
                "OA_XCODEGEN_DUPLICATE_ID",
                f"semantic id {semantic_id.value!r} duplicates {previous}",
                span=document.span(pointer),
            )


def _path_name(name: str) -> str:
    return "-".join(part.lower() for part in name.replace("_", " ").split()) or "group"
