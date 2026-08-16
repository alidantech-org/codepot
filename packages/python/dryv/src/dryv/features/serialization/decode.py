from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from importlib import import_module
from typing import Any

import yaml

from dryv.ir import Contract, Name, SemanticId
from dryv.versions import IR_API_VERSION

from .encode import FORMAT, IrCodecError, JsonValue, RepresentationRecord

_MAX_DEPTH = 128
_MAX_ITEMS = 500_000
_MAX_RECORD_BYTES = 1024 * 1024

public_ir = import_module("dryv.ir")
public_diagnostics = import_module("dryv.ir.diagnostics")


@dataclass(slots=True)
class _DecodeState:
    active: set[int] = field(default_factory=set)
    items: int = 0


def decode_contract(content: bytes, media_type: str) -> Contract:
    if _is_jsonl(media_type):
        return contract_from_jsonl(content)
    if _is_json(media_type):
        return contract_from_json(content)
    if _is_yaml(media_type):
        return contract_from_yaml(content)
    raise IrCodecError("IR_CODEC_MEDIA_TYPE", f"unsupported Canonical IR media type {media_type!r}")


def contract_from_json(value: str | bytes) -> Contract:
    try:
        text = value.decode("utf-8") if isinstance(value, bytes) else value
        document = json.loads(text, object_pairs_hook=_json_pairs)
    except UnicodeDecodeError as exc:
        raise IrCodecError("IR_CODEC_UTF8", "IR JSON must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise IrCodecError("IR_CODEC_JSON", f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    return contract_from_document(document)


def contract_from_yaml(value: str | bytes) -> Contract:
    try:
        text = value.decode("utf-8") if isinstance(value, bytes) else value
        document = yaml.load(text, Loader=_UniqueKeyLoader)
    except UnicodeDecodeError as exc:
        raise IrCodecError("IR_CODEC_UTF8", "IR YAML must be UTF-8") from exc
    except yaml.YAMLError as exc:
        raise IrCodecError("IR_CODEC_YAML", "IR YAML syntax is invalid") from exc
    return contract_from_document(document)


def contract_from_document(document: object) -> Contract:
    if not isinstance(document, dict) or not all(isinstance(key, str) for key in document):
        raise IrCodecError("IR_CODEC_ROOT", "IR transport root must be an object")
    unknown = sorted(set(document) - {"contract", "format", "irVersion"})
    if unknown:
        raise IrCodecError("IR_CODEC_UNKNOWN_FIELD", f"unknown transport field {unknown[0]!r}")
    if document.get("format") != FORMAT:
        raise IrCodecError("IR_CODEC_FORMAT", f"format must be {FORMAT!r}")
    if document.get("irVersion") != str(IR_API_VERSION):
        raise IrCodecError("IR_CODEC_VERSION", f"IR transport requires version {IR_API_VERSION}")
    value = _decode(document.get("contract"), path="$.contract", depth=0, state=_DecodeState())
    if not isinstance(value, Contract):
        raise IrCodecError("IR_CODEC_CONTRACT", "transport does not contain a Contract")
    return value


def contract_from_jsonl(content: bytes) -> Contract:
    records: dict[str, RepresentationRecord] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        if len(line) > _MAX_RECORD_BYTES:
            raise IrCodecError("IR_CODEC_RECORD_LIMIT", f"JSONL record {line_number} exceeds {_MAX_RECORD_BYTES} bytes")
        if len(records) >= _MAX_ITEMS:
            raise IrCodecError("IR_CODEC_LIMIT", f"JSONL exceeds {_MAX_ITEMS} records")
        try:
            raw = json.loads(line, object_pairs_hook=_json_pairs)
        except json.JSONDecodeError as exc:
            raise IrCodecError("IR_CODEC_JSONL", f"invalid JSONL record at line {line_number}") from exc
        if not isinstance(raw, dict) or set(raw) != {"id", "kind", "value"}:
            raise IrCodecError("IR_CODEC_RECORD", f"invalid JSONL record at line {line_number}")
        identity, kind, value = raw.get("id"), raw.get("kind"), raw.get("value")
        if not isinstance(identity, str) or not isinstance(kind, str) or not isinstance(value, dict):
            raise IrCodecError("IR_CODEC_RECORD", f"invalid JSONL record at line {line_number}")
        if identity in records:
            raise IrCodecError("IR_CODEC_DUPLICATE_RECORD", f"duplicate JSONL record id {identity!r}")
        records[identity] = RepresentationRecord(identity, kind, value)
    roots = [identity for identity, record in records.items() if record.kind == "Contract"]
    if len(roots) != 1:
        raise IrCodecError("IR_CODEC_RECORD_ROOT", "JSONL must contain exactly one Contract record")
    expanded = _expand_record(roots[0], records, active=set())
    return contract_from_document({"contract": expanded, "format": FORMAT, "irVersion": str(IR_API_VERSION)})


def _decode(value: object, *, path: str, depth: int, state: _DecodeState) -> object:
    state.items += 1
    if state.items > _MAX_ITEMS:
        raise IrCodecError("IR_CODEC_LIMIT", f"IR transport exceeds {_MAX_ITEMS} values", path=path)
    if depth > _MAX_DEPTH:
        raise IrCodecError("IR_CODEC_DEPTH", f"IR transport exceeds depth {_MAX_DEPTH}", path=path)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IrCodecError("IR_CODEC_NUMBER", "non-finite numbers are not supported", path=path)
        return value
    if isinstance(value, list):
        return tuple(_decode(item, path=f"{path}[{index}]", depth=depth + 1, state=state) for index, item in enumerate(value))
    if isinstance(value, dict):
        return _decode_object(value, path=path, depth=depth, state=state)
    raise IrCodecError("IR_CODEC_VALUE", f"unsupported decoded value {type(value).__name__}", path=path)


def _decode_object(value: dict[object, object], *, path: str, depth: int, state: _DecodeState) -> object:
    if not all(isinstance(key, str) for key in value):
        raise IrCodecError("IR_CODEC_KEY", "object keys must be strings", path=path)
    typed: dict[str, object] = value  # type: ignore[assignment]
    if "$ref" in typed:
        if set(typed) != {"$ref"} or not isinstance(typed["$ref"], str):
            raise IrCodecError("IR_CODEC_REF", "invalid semantic reference", path=path)
        return SemanticId(typed["$ref"])
    if "$name" in typed:
        if set(typed) != {"$name"} or not isinstance(typed["$name"], str):
            raise IrCodecError("IR_CODEC_NAME", "invalid semantic name", path=path)
        return Name(typed["$name"])
    if "$enum" in typed:
        enum_name = typed.get("$enum")
        if set(typed) != {"$enum", "value"} or not isinstance(enum_name, str):
            raise IrCodecError("IR_CODEC_ENUM", "invalid enum document", path=path)
        enum_type = _enum_registry().get(enum_name)
        if enum_type is None:
            raise IrCodecError("IR_CODEC_ENUM", f"unknown IR enum {enum_name!r}", path=path)
        try:
            return enum_type(typed["value"])
        except (TypeError, ValueError) as exc:
            raise IrCodecError("IR_CODEC_ENUM", "invalid enum value", path=path) from exc
    if "$type" in typed:
        type_name = typed.get("$type")
        if not isinstance(type_name, str):
            raise IrCodecError("IR_CODEC_TYPE", "IR type must be a string", path=path)
        target = _type_registry().get(type_name)
        if target is None:
            raise IrCodecError("IR_CODEC_TYPE", f"unknown IR record type {type_name!r}", path=path)
        allowed = {item.name for item in fields(target) if item.init and not item.name.startswith("_")}
        unknown = sorted(set(typed) - allowed - {"$type"})
        if unknown:
            raise IrCodecError("IR_CODEC_UNKNOWN_FIELD", f"unknown {type_name} field {unknown[0]!r}", path=path)
        kwargs = {
            key: _decode(item, path=f"{path}.{key}", depth=depth + 1, state=state)
            for key, item in typed.items()
            if key != "$type"
        }
        try:
            return target(**kwargs)
        except (TypeError, ValueError) as exc:
            raise IrCodecError("IR_CODEC_CONSTRUCTION", f"invalid {type_name} record", path=path) from exc
    return {key: _decode(typed[key], path=f"{path}.{key}", depth=depth + 1, state=state) for key in sorted(typed)}


def _type_registry() -> dict[str, type[Any]]:
    result: dict[str, type[Any]] = {}
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if isinstance(candidate, type) and is_dataclass(candidate):
                result[candidate.__name__] = candidate
    return result


def _enum_registry() -> dict[str, type[Enum]]:
    result: dict[str, type[Enum]] = {}
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if isinstance(candidate, type) and issubclass(candidate, Enum):
                result[candidate.__name__] = candidate
    return result


def _expand_record(identity: str, records: dict[str, RepresentationRecord], *, active: set[str]) -> JsonValue:
    record = records.get(identity)
    if record is None:
        raise IrCodecError("IR_CODEC_MISSING_RECORD", f"missing semantic record {identity!r}")
    if identity in active:
        raise IrCodecError("IR_CODEC_RECORD_CYCLE", f"semantic containment cycle includes {identity!r}")
    if record.value.get("$type") != record.kind:
        raise IrCodecError("IR_CODEC_RECORD_KIND", f"semantic record {identity!r} kind does not match its value")
    active.add(identity)
    try:
        return _expand_value(record.value, records, active=active)
    finally:
        active.remove(identity)


def _expand_value(value: JsonValue, records: dict[str, RepresentationRecord], *, active: set[str]) -> JsonValue:
    if isinstance(value, dict):
        if set(value) == {"$dryv", "id"} and value.get("$dryv") == "record-ref" and isinstance(value.get("id"), str):
            return _expand_record(value["id"], records, active=active)  # type: ignore[arg-type]
        return {key: _expand_value(item, records, active=active) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_expand_value(item, records, active=active) for item in value]
    return value


def _is_json(media_type: str) -> bool:
    return media_type in {"application/json", "application/dryv-ir+json"} or media_type.endswith("+json")


def _is_jsonl(media_type: str) -> bool:
    return media_type in {"application/jsonl", "application/x-ndjson", "application/dryv-ir+jsonl"} or media_type.endswith("+jsonl")


def _is_yaml(media_type: str) -> bool:
    return media_type in {"application/yaml", "application/x-yaml", "text/yaml", "application/dryv-ir+yaml"} or media_type.endswith("+yaml")


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise IrCodecError("IR_CODEC_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise IrCodecError("IR_CODEC_KEY", "YAML mapping keys must be strings")
        if key in result:
            raise IrCodecError("IR_CODEC_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)

__all__ = [
    "contract_from_document",
    "contract_from_json",
    "contract_from_jsonl",
    "contract_from_yaml",
    "decode_contract",
]
