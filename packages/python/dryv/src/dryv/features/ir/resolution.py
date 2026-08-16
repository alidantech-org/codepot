from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import fields, is_dataclass

from dryv.ir import SemanticId
from dryv.ir.model.schema_resolution import EffectiveSchema, resolve_effective_schema as _resolve_effective_schema


def dependency_graph(objects: Mapping[SemanticId, object]) -> dict[SemanticId, tuple[SemanticId, ...]]:
    known = set(objects)
    return {
        identity: tuple(sorted(_references(value, identity, known), key=str))
        for identity, value in sorted(objects.items(), key=lambda item: str(item[0]))
    }


def reverse_graph(dependencies: Mapping[SemanticId, tuple[SemanticId, ...]]) -> dict[SemanticId, tuple[SemanticId, ...]]:
    reverse: dict[SemanticId, list[SemanticId]] = defaultdict(list)
    for owner, values in dependencies.items():
        for dependency in values:
            reverse[dependency].append(owner)
    return {key: tuple(sorted(set(values), key=str)) for key, values in reverse.items()}


def effective_schema(semantic_id: SemanticId, schemas: Mapping[SemanticId, object]) -> EffectiveSchema:
    return _resolve_effective_schema(semantic_id, schemas)  # type: ignore[arg-type]


def _references(value: object, owner: SemanticId, known: set[SemanticId]) -> set[SemanticId]:
    if isinstance(value, SemanticId):
        return {value} if value != owner and value in known else set()
    if is_dataclass(value):
        identity = getattr(value, "id", None)
        if isinstance(identity, SemanticId) and identity != owner and identity in known:
            return {identity}
        result: set[SemanticId] = set()
        for item in fields(value):
            if item.name == "id":
                continue
            result.update(_references(getattr(value, item.name), owner, known))
        return result
    if isinstance(value, Mapping):
        result: set[SemanticId] = set()
        for item in value.values():
            result.update(_references(item, owner, known))
        return result
    if isinstance(value, (tuple, list, set, frozenset)):
        result: set[SemanticId] = set()
        for item in value:
            result.update(_references(item, owner, known))
        return result
    return set()


__all__ = ["dependency_graph", "effective_schema", "reverse_graph"]
