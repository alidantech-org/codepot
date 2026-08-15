from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, fields, is_dataclass
from typing import Generic, TypeVar

from dryv.diagnostics import Diagnostics
from dryv.ir import Contract, SemanticId, TriggerKind, walk_groups
from dryv.ir.model.schema_resolution import EffectiveSchema, resolve_effective_schema
from dryv.ir.validation import SemanticIndex, validate_contract

T = TypeVar("T")


class IRRuntimeError(ValueError):
    def __init__(self, code: str, message: str, *, semantic_id: SemanticId | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.semantic_id = semantic_id


@dataclass(frozen=True, slots=True)
class DerivedRelationships:
    event_emitters: Mapping[SemanticId, tuple[SemanticId, ...]]
    event_listeners: Mapping[SemanticId, tuple[SemanticId, ...]]
    schema_operations: Mapping[SemanticId, tuple[SemanticId, ...]]
    schema_storage_mappings: Mapping[SemanticId, tuple[SemanticId, ...]]
    view_presentations: Mapping[SemanticId, tuple[SemanticId, ...]]


@dataclass(frozen=True, slots=True)
class IRSnapshot:
    contract: Contract
    diagnostics: Diagnostics
    index: SemanticIndex
    objects: Mapping[SemanticId, object]
    dependencies: Mapping[SemanticId, tuple[SemanticId, ...]]
    dependents: Mapping[SemanticId, tuple[SemanticId, ...]]
    derived: DerivedRelationships

    @property
    def valid(self) -> bool:
        return not self.diagnostics.has_errors

    def get(self, semantic_id: SemanticId) -> object | None:
        return self.objects.get(semantic_id)

    def require(self, semantic_id: SemanticId) -> object:
        value = self.get(semantic_id)
        if value is None:
            raise IRRuntimeError(
                "IR_RUNTIME_MISSING_ID",
                f"unknown semantic id {semantic_id}",
                semantic_id=semantic_id,
            )
        return value

    def direct_dependencies(self, semantic_id: SemanticId) -> tuple[SemanticId, ...]:
        return self.dependencies.get(semantic_id, ())

    def direct_dependents(self, semantic_id: SemanticId) -> tuple[SemanticId, ...]:
        return self.dependents.get(semantic_id, ())

    def effective_schema(self, semantic_id: SemanticId) -> EffectiveSchema:
        if semantic_id not in self.index.schemas:
            raise IRRuntimeError(
                "IR_RUNTIME_NOT_SCHEMA",
                f"semantic id {semantic_id} is not a Schema",
                semantic_id=semantic_id,
            )
        return resolve_effective_schema(semantic_id, self.index.schemas)


class BoundedRecordIndex(Generic[T]):
    """Small id index for externally streamed canonical representation records."""

    def __init__(self, values: Mapping[str, T]) -> None:
        self._values = dict(values)

    @classmethod
    def from_records(
        cls,
        records: Iterable[T],
        *,
        id_of: Callable[[T], str],
        max_records: int = 500_000,
    ) -> BoundedRecordIndex[T]:
        values: dict[str, T] = {}
        for record in records:
            if len(values) >= max_records:
                raise IRRuntimeError("IR_RUNTIME_RECORD_LIMIT", f"record index exceeds {max_records} records")
            identity = id_of(record)
            if identity in values:
                raise IRRuntimeError("IR_RUNTIME_DUPLICATE_RECORD", f"duplicate record id {identity!r}")
            values[identity] = record
        return cls(values)

    def get(self, identity: str) -> T | None:
        return self._values.get(identity)

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._values))


class IRFeature:
    def load_contract(self, contract: Contract) -> IRSnapshot:
        diagnostics = validate_contract(contract)
        index, _ = SemanticIndex.build(contract)
        objects = _semantic_objects(contract, index)
        dependencies = _dependency_graph(objects)
        dependents = _reverse_graph(dependencies)
        derived = _derive(contract, index)
        return IRSnapshot(contract, diagnostics, index, objects, dependencies, dependents, derived)

    def load_records(
        self,
        records: Iterable[T],
        *,
        decoder: Callable[[Iterable[T]], Contract],
    ) -> IRSnapshot:
        """Load Serialization-owned records without importing a sibling Feature.

        Runtime supplies the Serialization decoder at composition time.
        """
        return self.load_contract(decoder(records))


def _semantic_objects(contract: Contract, index: SemanticIndex) -> dict[SemanticId, object]:
    objects: dict[SemanticId, object] = {contract.id: contract}
    for group in walk_groups(contract.groups):
        objects[group.id] = group
    for collection in (
        index.properties,
        index.schemas,
        index.fields,
        index.operations,
        index.views,
        index.storage,
        index.workflows,
        index.events,
        index.policies,
        index.failures,
        index.value_sources,
        index.presentations,
        index.presentation_entries,
    ):
        objects.update(collection)
    return objects


def _dependency_graph(objects: Mapping[SemanticId, object]) -> dict[SemanticId, tuple[SemanticId, ...]]:
    known = set(objects)
    return {
        semantic_id: tuple(sorted(_collect_refs(value, semantic_id, known), key=str))
        for semantic_id, value in sorted(objects.items(), key=lambda item: str(item[0]))
    }


def _collect_refs(value: object, owner: SemanticId, known: set[SemanticId]) -> set[SemanticId]:
    if isinstance(value, SemanticId):
        return {value} if value != owner and value in known else set()
    if is_dataclass(value):
        identity = getattr(value, "id", None)
        if isinstance(identity, SemanticId) and identity != owner and identity in known:
            return {identity}
        found: set[SemanticId] = set()
        for item in fields(value):
            if item.name == "id":
                continue
            found.update(_collect_refs(getattr(value, item.name), owner, known))
        return found
    if isinstance(value, Mapping):
        found: set[SemanticId] = set()
        for item in value.values():
            found.update(_collect_refs(item, owner, known))
        return found
    if isinstance(value, (tuple, list, set, frozenset)):
        found: set[SemanticId] = set()
        for item in value:
            found.update(_collect_refs(item, owner, known))
        return found
    return set()


def _reverse_graph(dependencies: Mapping[SemanticId, tuple[SemanticId, ...]]) -> dict[SemanticId, tuple[SemanticId, ...]]:
    reverse: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    for owner, values in dependencies.items():
        for dependency in values:
            reverse[dependency].append(owner)
    return {key: tuple(sorted(set(values), key=str)) for key, values in reverse.items()}


def _derive(contract: Contract, index: SemanticIndex) -> DerivedRelationships:
    event_emitters: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    event_listeners: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    schema_operations: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    schema_storage: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    view_presentations: dict[SemanticId, list[SemanticId]] = defaultdict(list)

    for operation in index.operations.values():
        for effect in operation.effects.events:
            event_emitters[effect.event].append(operation.id)
        if operation.facets.events is not None:
            for event_id in operation.facets.events.consumes:
                event_listeners[event_id].append(operation.id)
        trigger = operation.facets.trigger
        if trigger is not None and trigger.kind is TriggerKind.EVENT and trigger.event is not None:
            event_listeners[trigger.event].append(operation.id)
        schema_ids = set(operation.subjects)
        schema_ids.update(item.schema for item in operation.inputs)
        schema_ids.update(item.schema for item in operation.outputs if item.schema is not None)
        for schema_id in schema_ids:
            schema_operations[schema_id].append(operation.id)

    for mapping in index.storage.values():
        schema_storage[mapping.schema].append(mapping.id)

    for presentation in contract.presentations:
        for entry in presentation.entries:
            view_presentations[entry.view].append(presentation.id)

    return DerivedRelationships(
        event_emitters=_freeze_index(event_emitters),
        event_listeners=_freeze_index(event_listeners),
        schema_operations=_freeze_index(schema_operations),
        schema_storage_mappings=_freeze_index(schema_storage),
        view_presentations=_freeze_index(view_presentations),
    )


def _freeze_index(values: Mapping[SemanticId, list[SemanticId]]) -> dict[SemanticId, tuple[SemanticId, ...]]:
    return {key: tuple(sorted(set(items), key=str)) for key, items in values.items()}


__all__ = [
    "BoundedRecordIndex",
    "DerivedRelationships",
    "IRFeature",
    "IRRuntimeError",
    "IRSnapshot",
]
