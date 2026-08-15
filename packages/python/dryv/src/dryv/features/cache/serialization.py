from __future__ import annotations

import base64
import json
from dataclasses import asdict
from enum import Enum

from .model import CacheEntry


def cache_entry_bytes(entry: CacheEntry) -> bytes:
    """Encode one cache entry deterministically for replaceable persistence."""

    value = asdict(entry)
    value["payload"] = base64.b64encode(entry.payload).decode("ascii")
    normalized = _normalize(value)
    return json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _normalize(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, tuple | list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    raise TypeError(f"unsupported cache serialization value {type(value).__name__}")


__all__ = ["cache_entry_bytes"]
