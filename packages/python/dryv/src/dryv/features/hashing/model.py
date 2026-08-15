from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Mapping, Sequence, TypeAlias

CanonicalScalar: TypeAlias = str | int | float | bool | None
CanonicalValue: TypeAlias = CanonicalScalar | Sequence["CanonicalValue"] | Mapping[str, "CanonicalValue"]

HASH_ALGORITHM = "sha256"
HASH_VERSION = 1


class HashPurpose(StrEnum):
    RESOURCE_CONTENT = "resource-content"
    CANONICAL_DOCUMENT = "canonical-document"
    IR_RECORD = "ir-record"
    IR_BRANCH = "ir-branch"
    PACK_MANIFEST = "pack-manifest"
    TEMPLATE_CONTENT = "template-content"
    CONTEXT = "context"
    RENDERER_FINGERPRINT = "renderer-fingerprint"
    ARTIFACT_CONTENT = "artifact-content"
    BUILD_INPUT = "build-input"


@dataclass(frozen=True, slots=True, order=True)
class HashValue:
    purpose: HashPurpose
    digest: str
    algorithm: str = HASH_ALGORITHM
    version: int = HASH_VERSION

    def __post_init__(self) -> None:
        if self.algorithm != HASH_ALGORITHM:
            raise ValueError(f"unsupported hash algorithm {self.algorithm!r}")
        if self.version != HASH_VERSION:
            raise ValueError(f"unsupported hash version {self.version}")
        if len(self.digest) != 64 or any(ch not in "0123456789abcdef" for ch in self.digest):
            raise ValueError("hash digest must be a lowercase sha256 hex digest")

    @property
    def identity(self) -> str:
        return f"{self.algorithm}:v{self.version}:{self.purpose.value}:{self.digest}"


class HashingError(ValueError):
    def __init__(self, code: str, message: str, *, subject: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.subject = subject


def canonical_bytes(value: CanonicalValue) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def hash_bytes(purpose: HashPurpose, content: bytes) -> HashValue:
    return HashValue(purpose=purpose, digest=sha256(content).hexdigest())


def hash_value(purpose: HashPurpose, value: CanonicalValue) -> HashValue:
    return hash_bytes(purpose, canonical_bytes(value))


def hash_branch(
    root: str,
    record_hashes: Mapping[str, HashValue],
    dependencies: Mapping[str, Sequence[str]],
) -> HashValue:
    """Hash one semantic branch from already-canonical direct record hashes.

    Only dependencies reachable from ``root`` participate. Dependency ids are
    sorted before composition so callers can build indexes in any order.
    """

    cache: dict[str, str] = {}
    active: list[str] = []

    def visit(subject: str) -> str:
        cached = cache.get(subject)
        if cached is not None:
            return cached
        direct = record_hashes.get(subject)
        if direct is None:
            raise HashingError(
                "HASH_MISSING_RECORD",
                f"branch references missing direct record hash {subject!r}",
                subject=subject,
            )
        if subject in active:
            cycle = " -> ".join((*active[active.index(subject) :], subject))
            raise HashingError(
                "HASH_DEPENDENCY_CYCLE",
                f"semantic dependency cycle: {cycle}",
                subject=subject,
            )
        active.append(subject)
        try:
            children = tuple(sorted(set(dependencies.get(subject, ()))))
            child_hashes = tuple((child, visit(child)) for child in children)
            payload: CanonicalValue = {
                "direct": direct.identity,
                "dependencies": [[child, digest] for child, digest in child_hashes],
                "subject": subject,
            }
            digest = hash_value(HashPurpose.IR_BRANCH, payload).digest
            cache[subject] = digest
            return digest
        finally:
            active.pop()

    return HashValue(HashPurpose.IR_BRANCH, visit(root))


def hash_build_inputs(parts: Mapping[str, HashValue]) -> HashValue:
    payload: CanonicalValue = {
        "parts": [[name, value.identity] for name, value in sorted(parts.items())]
    }
    return hash_value(HashPurpose.BUILD_INPUT, payload)


def _normalize(value: CanonicalValue) -> CanonicalValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise HashingError("HASH_NON_FINITE_NUMBER", "canonical hashes reject non-finite numbers")
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise HashingError("HASH_INVALID_KEY", "canonical hash object keys must be strings")
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize(item) for item in value]
    raise HashingError("HASH_UNSUPPORTED_VALUE", f"unsupported canonical hash value {type(value).__name__}")


__all__ = [
    "CanonicalValue",
    "HASH_ALGORITHM",
    "HASH_VERSION",
    "HashPurpose",
    "HashValue",
    "HashingError",
    "canonical_bytes",
    "hash_branch",
    "hash_build_inputs",
    "hash_bytes",
    "hash_value",
]
