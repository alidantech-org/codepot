"""Deterministic portable representation mechanics for Dryv.

This Feature owns JSON, YAML and JSONL representation concerns. Semantic
validation remains in ``dryv.ir``.
"""

from .ir_codec import IrCodecError, contract_from_document, contract_from_json, contract_from_yaml, contract_to_document, contract_to_json, contract_to_yaml, validate_transport
from .records import RecordLocation, RepresentationRecord, SerializationError, canonical_json_bytes, canonicalize, decode_json, decode_resource_bytes, decode_yaml, encode_json, encode_jsonl, encode_yaml, iter_jsonl, iter_jsonl_indexed

__all__ = ["IrCodecError", "RecordLocation", "RepresentationRecord", "SerializationError", "canonical_json_bytes", "canonicalize", "contract_from_document", "contract_from_json", "contract_from_yaml", "contract_to_document", "contract_to_json", "contract_to_yaml", "decode_json", "decode_resource_bytes", "decode_yaml", "encode_json", "encode_jsonl", "encode_yaml", "iter_jsonl", "iter_jsonl_indexed", "validate_transport"]
