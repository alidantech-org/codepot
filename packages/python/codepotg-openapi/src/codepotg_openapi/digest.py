from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from codepotg.versions import IR_API_VERSION, PLUGIN_API_VERSION, BehaviorVersion

from .options import OpenApiOptions
from .version import PACKAGE_VERSION

ADAPTER_BEHAVIOR_VERSION = BehaviorVersion(1)
OPENAPI_VERSION_POLICY = "3.0.x|3.1.x"
X_CODEGEN_VERSION = "2"


@dataclass(frozen=True, slots=True)
class DigestDocument:
    identity: str
    value: object


def canonical_json(value: object) -> str:
    return json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def raw_digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def source_digest(
    *,
    documents: Sequence[DigestDocument],
    options: OpenApiOptions,
    reference_authority: str,
) -> str:
    payload = {
        "adapter": {
            "distributionVersion": PACKAGE_VERSION,
            "behaviorVersion": str(ADAPTER_BEHAVIOR_VERSION),
            "pluginApiVersion": str(PLUGIN_API_VERSION),
            "irApiVersion": str(IR_API_VERSION),
            "openapiVersionPolicy": OPENAPI_VERSION_POLICY,
            "xCodegenVersion": X_CODEGEN_VERSION,
        },
        "documents": [
            {"identity": item.identity, "semantic": item.value}
            for item in sorted(documents, key=lambda item: item.identity)
        ],
        "options": dict(options.canonical_items()),
        "referenceAuthority": reference_authority,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def semantic_signature(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _canonical(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple | list):
        return [_canonical(item) for item in value]
    if value is None or isinstance(value, str | int | bool):
        return value
    if isinstance(value, float):
        if value == 0:
            return 0
        return value
    raise TypeError(f"value is not JSON-compatible: {type(value).__name__}")
