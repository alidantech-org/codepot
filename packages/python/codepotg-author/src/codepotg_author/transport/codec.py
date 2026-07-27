from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

import yaml
from yaml.constructor import ConstructorError

from codepotg.ir import (
    AccessFacet,
    Compensation,
    Contract,
    Documentation,
    Event,
    EventEffect,
    EventsFacet,
    ExecutionFacet,
    ExecutionHook,
    ExecutionPhase,
    FieldConstraints,
    Group,
    GroupFacets,
    HttpFacet,
    KernelData,
    Name,
    Operation,
    OperationEffects,
    OperationFacets,
    OperationFailure,
    OperationOutput,
    Policy,
    Provenance,
    Schema,
    SchemaField,
    SchemaKind,
    SchemaUse,
    SemanticId,
    StorageFieldMapping,
    StorageMapping,
    TriggerFacet,
    TriggerKind,
    TypeExpression,
    TypeKind,
    View,
    ViewTrigger,
    Workflow,
    WorkflowDecisionCase,
    WorkflowFacets,
    WorkflowStep,
    WorkflowStepKind,
    WorkflowTransition,
    validate_contract,
)

FORMAT = "codepotg.ir"
VERSION = 1

_TYPES = {
    cls.__name__: cls
    for cls in (
        AccessFacet,
        Compensation,
        Contract,
        Documentation,
        Event,
        EventEffect,
        EventsFacet,
        ExecutionFacet,
        ExecutionHook,
        FieldConstraints,
        Group,
        GroupFacets,
        HttpFacet,
        KernelData,
        Name,
        Operation,
        OperationEffects,
        OperationFacets,
        OperationFailure,
        OperationOutput,
        Policy,
        Provenance,
        Schema,
        SchemaField,
        SchemaUse,
        SemanticId,
        StorageFieldMapping,
        StorageMapping,
        TriggerFacet,
        TypeExpression,
        View,
        ViewTrigger,
        Workflow,
        WorkflowDecisionCase,
        WorkflowFacets,
        WorkflowStep,
        WorkflowTransition,
    )
}
_ENUMS = {
    cls.__name__: cls
    for cls in (ExecutionPhase, SchemaKind, TriggerKind, TypeKind, WorkflowStepKind)
}


class DuplicateSafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: DuplicateSafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


DuplicateSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def to_document(contract: Contract) -> dict[str, object]:
    diagnostics = validate_contract(contract)
    if diagnostics.has_errors:
        raise ValueError("cannot encode an invalid contract")
    return {"format": FORMAT, "version": VERSION, "contract": _encode(contract)}


def from_document(document: object) -> Contract:
    if not isinstance(document, dict):
        raise TypeError("IR document must be an object")
    expected = {"format", "version", "contract"}
    unknown = set(document) - expected
    missing = expected - set(document)
    if unknown:
        raise ValueError(f"unknown IR document fields: {', '.join(sorted(unknown))}")
    if missing:
        raise ValueError(f"missing IR document fields: {', '.join(sorted(missing))}")
    if document["format"] != FORMAT:
        raise ValueError("unsupported IR document format")
    if document["version"] != VERSION:
        raise ValueError("unsupported IR document version")
    contract = _decode(document["contract"])
    if not isinstance(contract, Contract):
        raise TypeError("IR document contract payload did not decode to Contract")
    diagnostics = validate_contract(contract)
    if diagnostics.has_errors:
        raise ValueError("decoded contract failed core validation")
    return contract


def dumps_json(contract: Contract) -> str:
    return json.dumps(to_document(contract), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def loads_json(value: str | bytes) -> Contract:
    return from_document(json.loads(value))


def dumps_yaml(contract: Contract) -> str:
    return yaml.safe_dump(to_document(contract), sort_keys=True, allow_unicode=True)


def loads_yaml(value: str | bytes) -> Contract:
    loaded = yaml.load(value, Loader=DuplicateSafeLoader)
    return from_document(loaded)


def _encode(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Enum):
        return {"$enum": value.__class__.__name__, "value": value.value}
    if isinstance(value, tuple):
        return {"$tuple": [_encode(item) for item in value]}
    if is_dataclass(value) and not isinstance(value, type):
        result: dict[str, object] = {"$type": value.__class__.__name__}
        for item in fields(value):
            result[item.name] = _encode(getattr(value, item.name))
        return result
    raise TypeError(f"unsupported IR transport value: {type(value).__name__}")


def _decode(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, list):
        raise TypeError("untagged arrays are not valid canonical IR values")
    if not isinstance(value, dict):
        raise TypeError(f"unsupported canonical value: {type(value).__name__}")
    if set(value) == {"$tuple"}:
        items = value["$tuple"]
        if not isinstance(items, list):
            raise TypeError("$tuple must contain a list")
        return tuple(_decode(item) for item in items)
    if "$enum" in value:
        if set(value) != {"$enum", "value"}:
            raise ValueError("enum values contain unknown fields")
        enum_name = value["$enum"]
        if not isinstance(enum_name, str) or enum_name not in _ENUMS:
            raise ValueError(f"unknown IR enum type: {enum_name!r}")
        return _ENUMS[enum_name](value["value"])
    type_name = value.get("$type")
    if not isinstance(type_name, str) or type_name not in _TYPES:
        raise ValueError(f"unknown IR value type: {type_name!r}")
    cls = _TYPES[type_name]
    allowed = {item.name for item in fields(cls)}
    supplied = set(value) - {"$type"}
    unknown = supplied - allowed
    if unknown:
        raise ValueError(f"unknown fields for {type_name}: {', '.join(sorted(unknown))}")
    kwargs = {key: _decode(item) for key, item in value.items() if key != "$type"}
    return cls(**kwargs)
