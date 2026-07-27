from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import Field, fields, is_dataclass
from enum import Enum
from typing import Any, cast

import yaml
from codepotg.diagnostics import SourceIdentity, SourceKind, SourcePosition, SourceSpan
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
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode, Node

FORMAT = "codepotg.ir"
VERSION = 1

Factory = Callable[..., object]
Constructor = Callable[..., object]

_TYPES: dict[str, Factory] = {
    cls.__name__: cast(Factory, cls)
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
        SourceIdentity,
        SourcePosition,
        SourceSpan,
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
_ENUMS: dict[str, type[Enum]] = {
    cls.__name__: cls
    for cls in (
        ExecutionPhase,
        SchemaKind,
        SourceKind,
        TriggerKind,
        TypeKind,
        WorkflowStepKind,
    )
}


class DuplicateSafeLoader(yaml.SafeLoader):
    pass


def _construct_object(loader: DuplicateSafeLoader, node: Node, *, deep: bool) -> object:
    constructor = cast(Constructor, loader.construct_object)
    return constructor(node, deep=deep)


def _construct_mapping(
    loader: DuplicateSafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = _construct_object(loader, key_node, deep=deep)
        if key in result:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = _construct_object(loader, value_node, deep=deep)
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
    typed_document = cast(dict[str, object], document)
    expected = {"format", "version", "contract"}
    supplied = set(typed_document)
    unknown = supplied - expected
    missing = expected - supplied
    if unknown:
        raise ValueError(f"unknown IR document fields: {', '.join(sorted(unknown))}")
    if missing:
        raise ValueError(f"missing IR document fields: {', '.join(sorted(missing))}")
    if typed_document["format"] != FORMAT:
        raise ValueError("unsupported IR document format")
    if typed_document["version"] != VERSION:
        raise ValueError("unsupported IR document version")
    contract = _decode(typed_document["contract"])
    if not isinstance(contract, Contract):
        raise TypeError("IR document contract payload did not decode to Contract")
    diagnostics = validate_contract(contract)
    if diagnostics.has_errors:
        raise ValueError("decoded contract failed core validation")
    return contract


def dumps_json(contract: Contract) -> str:
    return json.dumps(
        to_document(contract),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def loads_json(value: str | bytes) -> Contract:
    return from_document(json.loads(value, object_pairs_hook=_unique_pairs))


def dumps_yaml(contract: Contract) -> str:
    return yaml.safe_dump(to_document(contract), sort_keys=True, allow_unicode=True)


def loads_yaml(value: str | bytes) -> Contract:
    return from_document(yaml.load(value, Loader=DuplicateSafeLoader))


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def _init_fields(cls: type[object]) -> tuple[Field[Any], ...]:
    return tuple(item for item in fields(cast(Any, cls)) if item.init)


def _encode(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, Enum):
        return {"$enum": value.__class__.__name__, "value": value.value}
    if isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, tuple):
        return {"$tuple": [_encode(item) for item in value]}
    if is_dataclass(value) and not isinstance(value, type):
        result: dict[str, object] = {"$type": value.__class__.__name__}
        for item in _init_fields(value.__class__):
            field_value = cast(object, getattr(value, item.name))
            result[item.name] = _encode(field_value)
        return result
    raise TypeError(f"unsupported IR transport value: {type(value).__name__}")


def _decode(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, list):
        raise TypeError("untagged arrays are not valid canonical IR values")
    if not isinstance(value, dict):
        raise TypeError(f"unsupported canonical value: {type(value).__name__}")
    typed_value = cast(dict[str, object], value)
    keys = set(typed_value)
    if keys == {"$tuple"}:
        items = typed_value["$tuple"]
        if not isinstance(items, list):
            raise TypeError("$tuple must contain a list")
        return tuple(_decode(item) for item in cast(list[object], items))
    if "$enum" in typed_value:
        if keys != {"$enum", "value"}:
            raise ValueError("enum values contain unknown fields")
        enum_name = typed_value["$enum"]
        if not isinstance(enum_name, str) or enum_name not in _ENUMS:
            raise ValueError(f"unknown IR enum type: {enum_name!r}")
        return _ENUMS[enum_name](typed_value["value"])
    type_name = typed_value.get("$type")
    if not isinstance(type_name, str) or type_name not in _TYPES:
        raise ValueError(f"unknown IR value type: {type_name!r}")
    factory = _TYPES[type_name]
    allowed = {item.name for item in _init_fields(cast(type[object], factory))}
    supplied = keys - {"$type"}
    unknown = supplied - allowed
    if unknown:
        raise ValueError(f"unknown fields for {type_name}: {', '.join(sorted(unknown))}")
    kwargs: dict[str, object] = {
        key: _decode(item) for key, item in typed_value.items() if key != "$type"
    }
    return factory(**kwargs)
