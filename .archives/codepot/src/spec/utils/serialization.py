"""Stable serialization helpers for repository hashing/debug output."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from archives.codepot.src.spec.utils.constants import HASH_JSON_ENCODING, HASH_JSON_SEPARATORS
from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    """Convert known typed values into deterministic JSON-compatible data.

    This is a low-level serialization utility. Normal repository logic should
    not walk raw dictionaries directly.
    """

    if isinstance(value, BaseModel):
        return to_jsonable(value.model_dump(mode="json", exclude_none=True))

    if is_dataclass(value) and not isinstance(value, type):
        return to_jsonable(asdict(value))

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return value.as_posix()

    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }

    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]

    if isinstance(value, str | int | float | bool) or value is None:
        return value

    return str(value)


def stable_json(value: Any) -> str:
    """Serialize a value to stable compact JSON text."""

    return json.dumps(
        to_jsonable(value),
        sort_keys=True,
        separators=HASH_JSON_SEPARATORS,
        ensure_ascii=False,
    )


def stable_json_bytes(value: Any) -> bytes:
    """Serialize a value to stable JSON bytes."""

    return stable_json(value).encode(HASH_JSON_ENCODING)
