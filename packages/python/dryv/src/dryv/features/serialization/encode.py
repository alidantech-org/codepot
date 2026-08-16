from __future__ import annotations

import json
import math
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from hashlib import sha256
from typing import TypeAlias

import yaml

from dryv.ir import Contract, Name, SemanticId
from dryv.versions import IR_API_VERSION

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

FORMAT = "codepot-ir"
_RECORD_REF_MARKER = "$dryv"
_RECORD_REF_KIND = "record-ref"


class IrCodecError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


@dataclass(frozen=True, slots=True)
class RepresentationRecord:
    id: str
    kind: str
    value: dict[str, JsonValue]


def encode_value(value: object) -> JsonValue:
    if isinstance(value, Enum):
        return {"$enum": type(value).__name__, "value": encode_value(value.value)}
    if isinstance(value, SemanticId):
        return {"$ref": value.value}
    if isinstance(value, Name):
        return {"$name": value.value}
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IrCodecError("IR_CODEC_NUMBER", "non-finite numbers are not supported")
        return value
    if isinstance(value, (tuple, list)):
        return [encode_value(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise IrCodecError("IR_CODEC_KEY", "object keys must be strings")
        return {key: encode_value(value[key]) for key in sorted(value)}
    if is_dataclass(value):
        result: dict[str, JsonValue] = {"$type": type(value).__name__}
        for item in fields(value):
            if item.init and not item.name.startswith("_"):
                result[item.name] = encode_value(getattr(value, item.name))
        return result
    raise IrCodecError("IR_CODEC_VALUE", f"unsupported canonical value {type(value).__name__}")


def contract_to_document(contract: Contract) -> dict[str, JsonValue]:
    return {
        "contract": encode_value(contract),
        "format": FORMAT,
        "irVersion": str(IR_API_VERSION),
    }


def contract_to_json(contract: Contract, *, pretty: bool = True) -> str:
    return json.dumps(
        contract_to_document(contract),
        ensure_ascii=False,
        allow_nan=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    ) + ("\n" if pretty else "")


def contract_to_yaml(contract: Contract) -> str:
    return yaml.safe_dump(
        contract_to_document(contract),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
    )


def contract_to_records(contract: Contract) -> tuple[RepresentationRecord, ...]:
    encoded = contract_to_document(contract)["contract"]
    records: dict[str, RepresentationRecord] = {}
    root = _extract_records(encoded, records)
    if not _is_record_ref(root):
        raise IrCodecError("IR_CODEC_RECORD_ROOT", "canonical Contract did not produce a semantic root record")
    return tuple(records[key] for key in sorted(records))


def contract_to_jsonl(contract: Contract) -> bytes:
    lines = [
        json.dumps(
            {"id": record.id, "kind": record.kind, "value": record.value},
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        for record in contract_to_records(contract)
    ]
    return b"\n".join(lines) + (b"\n" if lines else b"")


def canonical_record_bytes(record: RepresentationRecord) -> bytes:
    return json.dumps(
        {"id": record.id, "kind": record.kind, "value": record.value},
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_record_hash(record: RepresentationRecord) -> str:
    return f"sha256:{sha256(canonical_record_bytes(record)).hexdigest()}"


def _extract_records(value: JsonValue, records: dict[str, RepresentationRecord]) -> JsonValue:
    if isinstance(value, dict):
        record_id = _semantic_record_id(value)
        if record_id is not None:
            kind = value.get("$type")
            assert isinstance(kind, str)
            payload = {key: _extract_records(item, records) for key, item in sorted(value.items())}
            if record_id in records:
                raise IrCodecError("IR_CODEC_DUPLICATE_RECORD", f"duplicate semantic record id {record_id!r}")
            records[record_id] = RepresentationRecord(record_id, kind, payload)
            return {_RECORD_REF_MARKER: _RECORD_REF_KIND, "id": record_id}
        return {key: _extract_records(item, records) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_extract_records(item, records) for item in value]
    return value


def _semantic_record_id(value: dict[str, JsonValue]) -> str | None:
    if not isinstance(value.get("$type"), str):
        return None
    identity = value.get("id")
    if not isinstance(identity, dict) or set(identity) != {"$ref"}:
        return None
    result = identity.get("$ref")
    return result if isinstance(result, str) else None


def _is_record_ref(value: JsonValue) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {_RECORD_REF_MARKER, "id"}
        and value.get(_RECORD_REF_MARKER) == _RECORD_REF_KIND
        and isinstance(value.get("id"), str)
    )


__all__ = [
    "FORMAT",
    "IrCodecError",
    "JsonValue",
    "RepresentationRecord",
    "canonical_record_bytes",
    "canonical_record_hash",
    "contract_to_document",
    "contract_to_json",
    "contract_to_jsonl",
    "contract_to_records",
    "contract_to_yaml",
    "encode_value",
]
