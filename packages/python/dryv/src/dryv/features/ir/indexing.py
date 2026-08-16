from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from dryv.ir import Contract, SemanticId, walk_groups
from dryv.ir.diagnostics import Diagnostics
from dryv.ir.model.validation import SemanticIndex


@dataclass(frozen=True, slots=True)
class IRSnapshot:
    contract: Contract
    diagnostics: Diagnostics
    semantic_index: SemanticIndex
    objects: Mapping[SemanticId, object]
    kinds: Mapping[SemanticId, str]
    dependencies: Mapping[SemanticId, tuple[SemanticId, ...]]
    dependents: Mapping[SemanticId, tuple[SemanticId, ...]]

    @property
    def valid(self) -> bool:
        return not self.diagnostics.has_errors

    def require(self, semantic_id: SemanticId) -> object:
        value = self.objects.get(semantic_id)
        if value is None:
            raise KeyError(str(semantic_id))
        return value

    def kind(self, semantic_id: SemanticId) -> str:
        value = self.kinds.get(semantic_id)
        if value is None:
            raise KeyError(str(semantic_id))
        return value


def build_object_index(contract: Contract, semantic_index: SemanticIndex) -> tuple[dict[SemanticId, object], dict[SemanticId, str]]:
    objects: dict[SemanticId, object] = {contract.id: contract}
    kinds: dict[SemanticId, str] = {contract.id: "contract"}

    for group in walk_groups(contract.groups):
        objects[group.id] = group
        kinds[group.id] = "group"

    collections = (
        (semantic_index.properties, "property"),
        (semantic_index.schemas, "schema"),
        (semantic_index.fields, "schema_field"),
        (semantic_index.operations, "operation"),
        (semantic_index.views, "view"),
        (semantic_index.storage, "storage_mapping"),
        (semantic_index.workflows, "workflow"),
        (semantic_index.events, "event"),
        (semantic_index.policies, "policy"),
        (semantic_index.failures, "failure"),
        (semantic_index.value_sources, "value_source"),
        (semantic_index.presentations, "presentation"),
        (semantic_index.presentation_entries, "presentation_entry"),
    )
    for collection, kind in collections:
        objects.update(collection)
        kinds.update({identity: kind for identity in collection})
    return objects, kinds


__all__ = ["IRSnapshot", "build_object_index"]
