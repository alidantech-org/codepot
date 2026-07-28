from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="strict")).hexdigest()


def stable_identity(parts: Iterable[object]) -> str:
    encoded = json.dumps(
        tuple(parts),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
