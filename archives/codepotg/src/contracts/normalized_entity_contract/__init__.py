"""Import-safe normalized entity contract.

The sibling compatibility module exposes a public rule property named ``field``.
Inside that dataclass body, the property name shadows ``dataclasses.field`` before
``raw_arguments`` is declared. Load the established implementation with that one
constructor qualified explicitly, preserving every public class and function.

The real Codepot fixture uses resource-grouped entities such as
``x-codegen.entities.apps.App``. The original normalized builder accepts a flat
entity registry, so this package boundary converts both authored shapes into one
canonical flat view before invoking the established implementation.
"""

from __future__ import annotations

from collections.abc import Mapping as _CompatMapping
from pathlib import Path
from typing import Any as _CompatAny

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_entity_contract.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
_SHADOWED_DECLARATION = "raw_arguments: FrozenMap = field(default_factory=FrozenMap)"
_QUALIFIED_DECLARATION = (
    "raw_arguments: FrozenMap = "
    "__import__('dataclasses').field(default_factory=FrozenMap)"
)

if _SOURCE.count(_SHADOWED_DECLARATION) != 1:
    raise RuntimeError(
        "Normalized entity compatibility source no longer has the expected "
        "dataclass field declaration"
    )

_SOURCE = _SOURCE.replace(
    _SHADOWED_DECLARATION,
    _QUALIFIED_DECLARATION,
    1,
)
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102

_ORIGINAL_BUILD_NORMALIZED_ENTITY_CONTRACT = build_normalized_entity_contract


def build_normalized_entity_contract(api, raw):
    """Build normalized entities from flat or resource-grouped Codepot metadata."""
    return _ORIGINAL_BUILD_NORMALIZED_ENTITY_CONTRACT(
        api,
        _compat_normalize_document(raw),
    )


def _compat_normalize_document(
    raw: _CompatMapping[str, _CompatAny] | None,
) -> _CompatMapping[str, _CompatAny] | None:
    if not isinstance(raw, _CompatMapping):
        return raw
    codegen = raw.get("x-codegen")
    if not isinstance(codegen, _CompatMapping):
        return raw

    entities = codegen.get("entities")
    base_entities = codegen.get("baseEntities")
    normalized_entities = _compat_flatten_entities(entities)
    normalized_bases = _compat_normalize_entity_map(base_entities)

    if normalized_entities is entities and normalized_bases is base_entities:
        return raw

    normalized_codegen = dict(codegen)
    if normalized_entities is not entities:
        normalized_codegen["entities"] = normalized_entities
    if normalized_bases is not base_entities:
        normalized_codegen["baseEntities"] = normalized_bases
    normalized_document = dict(raw)
    normalized_document["x-codegen"] = normalized_codegen
    return normalized_document


def _compat_flatten_entities(value: _CompatAny) -> _CompatAny:
    if not isinstance(value, _CompatMapping):
        return value

    flattened: dict[str, _CompatAny] = {}
    changed = False
    for owner, candidate in value.items():
        if not isinstance(candidate, _CompatMapping):
            continue
        if _compat_is_entity_definition(candidate):
            flattened[str(owner)] = _compat_normalize_entity(candidate)
            changed = changed or flattened[str(owner)] != candidate
            continue

        nested_values = [
            (str(name), item)
            for name, item in candidate.items()
            if isinstance(item, _CompatMapping)
            and _compat_is_entity_definition(item)
        ]
        if not nested_values:
            flattened[str(owner)] = candidate
            continue

        changed = True
        for name, entity in nested_values:
            flattened[name] = _compat_normalize_entity(
                entity,
                resource_hint=str(owner),
            )

    return flattened if changed else value


def _compat_normalize_entity_map(value: _CompatAny) -> _CompatAny:
    if not isinstance(value, _CompatMapping):
        return value
    normalized = {
        str(name): _compat_normalize_entity(item)
        if isinstance(item, _CompatMapping)
        else item
        for name, item in value.items()
    }
    return normalized if normalized != value else value


def _compat_normalize_entity(
    value: _CompatMapping[str, _CompatAny],
    *,
    resource_hint: str | None = None,
) -> dict[str, _CompatAny]:
    normalized = dict(value)
    resource = _compat_reference_name(normalized.get("resource"))
    if resource is not None:
        normalized["resource"] = resource
    elif resource_hint is not None:
        normalized["resource"] = resource_hint

    extends = _compat_reference_sequence(normalized.get("extends"))
    if extends:
        normalized["extends"] = list(extends)

    for key in ("fields", "backendFields", "backend"):
        fields = normalized.get(key)
        if isinstance(fields, _CompatMapping):
            normalized[key] = {
                str(name): _compat_normalize_field(item)
                if isinstance(item, _CompatMapping)
                else item
                for name, item in fields.items()
            }

    relations = normalized.get("relations")
    if isinstance(relations, _CompatMapping):
        normalized["relations"] = {
            str(name): _compat_normalize_relation(item)
            if isinstance(item, _CompatMapping)
            else item
            for name, item in relations.items()
        }
    elif isinstance(relations, list | tuple):
        normalized["relations"] = [
            _compat_normalize_relation(item)
            if isinstance(item, _CompatMapping)
            else item
            for item in relations
        ]
    return normalized


def _compat_normalize_field(
    value: _CompatMapping[str, _CompatAny],
) -> dict[str, _CompatAny]:
    normalized = dict(value)
    reference = normalized.get("$ref")
    if isinstance(reference, str) and "schema" not in normalized:
        normalized["schema"] = {"$ref": reference}
    if "edit" in normalized and "editable" not in normalized:
        normalized["editable"] = normalized["edit"]
    if "select" in normalized and "selectable" not in normalized:
        normalized["selectable"] = normalized["select"]
    return normalized


def _compat_normalize_relation(
    value: _CompatMapping[str, _CompatAny],
) -> dict[str, _CompatAny]:
    normalized = dict(value)
    target = normalized.get("targetEntity", normalized.get("target"))
    target_name = _compat_reference_name(target)
    if target_name is not None:
        normalized["targetEntity"] = target_name

    cardinality = normalized.get("cardinality", normalized.get("kind"))
    if isinstance(cardinality, str):
        normalized["cardinality"] = _CARDINALITY_ALIASES.get(
            cardinality,
            cardinality,
        )

    for key in ("onDelete", "onUpdate"):
        action = normalized.get(key)
        if isinstance(action, _CompatMapping):
            selected = next(
                (
                    str(name)
                    for name, enabled in action.items()
                    if enabled is True
                ),
                None,
            )
            if selected is not None:
                normalized[key] = selected
    return normalized


def _compat_reference_sequence(value: _CompatAny) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, _CompatMapping):
        name = _compat_reference_name(value)
        return (name,) if name is not None else ()
    if isinstance(value, list | tuple):
        return tuple(
            name
            for item in value
            if (name := _compat_reference_name(item)) is not None
        )
    return ()


def _compat_reference_name(value: _CompatAny) -> str | None:
    if isinstance(value, str):
        return value.rsplit("/", 1)[-1] if value else None
    if not isinstance(value, _CompatMapping):
        return None
    key = value.get("key")
    if isinstance(key, str) and key:
        return key
    reference = value.get("$ref")
    if isinstance(reference, str) and reference:
        return reference.rsplit("/", 1)[-1]
    name = value.get("name")
    return name if isinstance(name, str) and name else None


def _compat_is_entity_definition(value: _CompatMapping[str, _CompatAny]) -> bool:
    return bool(_ENTITY_DEFINITION_KEYS.intersection(value))


_CARDINALITY_ALIASES = {
    "belongsTo": "many_to_one",
    "hasMany": "one_to_many",
    "hasOne": "one_to_one",
    "manyToMany": "many_to_many",
}
_ENTITY_DEFINITION_KEYS = {
    "kind",
    "resource",
    "schema",
    "store",
    "table",
    "visibility",
    "extends",
    "fields",
    "backendFields",
    "backend",
    "relations",
    "constraints",
    "indexes",
    "unique",
}


del _QUALIFIED_DECLARATION
del _SHADOWED_DECLARATION
del _SOURCE
del _SOURCE_PATH
