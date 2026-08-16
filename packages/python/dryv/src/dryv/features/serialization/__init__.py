"""Canonical Dryv IR JSON, YAML and JSONL representation mechanics."""

from .decode import (
    contract_from_document,
    contract_from_json,
    contract_from_jsonl,
    contract_from_yaml,
    decode_contract,
)
from .encode import (
    FORMAT,
    IrCodecError,
    JsonValue,
    RepresentationRecord,
    canonical_record_bytes,
    canonical_record_hash,
    contract_to_document,
    contract_to_json,
    contract_to_jsonl,
    contract_to_records,
    contract_to_yaml,
    encode_value,
)

__all__ = [
    "FORMAT",
    "IrCodecError",
    "JsonValue",
    "RepresentationRecord",
    "canonical_record_bytes",
    "canonical_record_hash",
    "contract_from_document",
    "contract_from_json",
    "contract_from_jsonl",
    "contract_from_yaml",
    "contract_to_document",
    "contract_to_json",
    "contract_to_jsonl",
    "contract_to_records",
    "contract_to_yaml",
    "decode_contract",
    "encode_value",
]
