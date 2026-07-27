from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TypeAlias

from codepotg.diagnostics import SourceSpan

JsonScalar: TypeAlias = str | int | float | bool | None
FrozenValue: TypeAlias = (
    JsonScalar | tuple["FrozenValue", ...] | tuple[tuple[str, "FrozenValue"], ...]
)
FrozenObject: TypeAlias = tuple[tuple[str, FrozenValue], ...]

_SEMANTIC_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")


@dataclass(frozen=True, slots=True, order=True)
class SemanticId:
    value: str

    def __post_init__(self) -> None:
        if _SEMANTIC_ID.fullmatch(self.value) is None:
            raise ValueError(f"invalid semantic id: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Documentation:
    summary: str | None = None
    description: str | None = None
    external_url: str | None = None


@dataclass(frozen=True, slots=True)
class Provenance:
    source_kind: str
    source_id: str
    pointer: str | None = None
    span: SourceSpan | None = None

    def __post_init__(self) -> None:
        if not self.source_kind or not self.source_id:
            raise ValueError("provenance requires source_kind and source_id")


@dataclass(frozen=True, slots=True)
class KernelData:
    documentation: Documentation = field(default_factory=Documentation)
    provenance: Provenance | None = None
    extensions: FrozenObject = ()
    raw: FrozenObject = ()

    def __post_init__(self) -> None:
        validate_frozen_object("extensions", self.extensions)
        validate_frozen_object("raw", self.raw)


def semantic_id(value: SemanticId | str) -> SemanticId:
    return value if isinstance(value, SemanticId) else SemanticId(value)


def validate_frozen_object(label: str, value: FrozenObject) -> None:
    keys = tuple(key for key, _ in value)
    if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
        raise ValueError(f"{label} must be sorted by unique key")
    for key, item in value:
        if not key:
            raise ValueError(f"{label} keys must not be empty")
        _validate_frozen_value(label, item)


def _validate_frozen_value(label: str, value: FrozenValue) -> None:
    if isinstance(value, tuple):
        if value and all(isinstance(item, tuple) and len(item) == 2 for item in value):
            validate_frozen_object(label, value)  # type: ignore[arg-type]
            return
        for item in value:
            _validate_frozen_value(label, item)
