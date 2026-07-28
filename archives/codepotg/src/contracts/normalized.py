from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Generic, TypeVar

from archives.codepotg.src.contracts.source import FrozenMap, freeze_source_map, freeze_source_value

T = TypeVar("T")


class ValueOrigin(StrEnum):
    """Where a normalized value came from."""

    MISSING = "missing"
    AUTHORED = "authored"
    INFERRED = "inferred"
    DERIVED = "derived"
    EFFECTIVE = "effective"


@dataclass(frozen=True)
class PresenceValue(Generic[T]):
    """Value that distinguishes missing, explicit null, and effective origins."""

    value: T | None = None
    is_set: bool = False
    origin: ValueOrigin = ValueOrigin.MISSING
    source_path: str = ""

    @property
    def is_authored(self) -> bool:
        return self.is_set and self.origin == ValueOrigin.AUTHORED

    @property
    def is_inferred(self) -> bool:
        return self.is_set and self.origin == ValueOrigin.INFERRED

    @property
    def is_derived(self) -> bool:
        return self.is_set and self.origin == ValueOrigin.DERIVED

    @property
    def is_effective(self) -> bool:
        return self.is_set and self.origin == ValueOrigin.EFFECTIVE

    @property
    def is_null(self) -> bool:
        return self.is_set and self.value is None

    @classmethod
    def missing(cls, *, source_path: str = "") -> PresenceValue[T]:
        return cls(source_path=source_path)

    @classmethod
    def authored(
        cls,
        value: T | None,
        *,
        source_path: str = "",
    ) -> PresenceValue[T]:
        return cls(
            value=freeze_source_value(value),
            is_set=True,
            origin=ValueOrigin.AUTHORED,
            source_path=source_path,
        )

    @classmethod
    def inferred(
        cls,
        value: T | None,
        *,
        source_path: str = "",
    ) -> PresenceValue[T]:
        return cls(
            value=freeze_source_value(value),
            is_set=True,
            origin=ValueOrigin.INFERRED,
            source_path=source_path,
        )

    @classmethod
    def derived(
        cls,
        value: T | None,
        *,
        source_path: str = "",
    ) -> PresenceValue[T]:
        return cls(
            value=freeze_source_value(value),
            is_set=True,
            origin=ValueOrigin.DERIVED,
            source_path=source_path,
        )

    @classmethod
    def effective(
        cls,
        value: T | None,
        *,
        source_path: str = "",
    ) -> PresenceValue[T]:
        return cls(
            value=freeze_source_value(value),
            is_set=True,
            origin=ValueOrigin.EFFECTIVE,
            source_path=source_path,
        )


class DiagnosticCategory(StrEnum):
    """Stable normalized-contract diagnostic categories."""

    UNRESOLVED = "unresolved"
    RAW_ONLY = "raw_only"
    UNSUPPORTED = "unsupported"
    MALFORMED = "malformed"
    DEPRECATED = "deprecated"
    LOST = "lost"
    COLLISION = "collision"
    CYCLE = "cycle"


class DiagnosticLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ContractDiagnostic:
    """One normalized source-preservation or resolution diagnostic."""

    category: DiagnosticCategory
    message: str
    source_path: str = ""
    level: DiagnosticLevel = DiagnosticLevel.WARNING
    value: Any = None
    ref: str | None = None
    owner: str | None = None
    meta: FrozenMap = field(default_factory=FrozenMap)


class ReferenceKind(StrEnum):
    UNKNOWN = "unknown"
    SCHEMA = "schema"
    RESOURCE = "resource"
    ENTITY = "entity"
    OPERATION = "operation"
    COMPONENT = "component"
    PARAMETER = "parameter"
    REQUEST_BODY = "request_body"
    RESPONSE = "response"
    ACCESS = "access"
    HOOK = "hook"
    FRONTEND = "frontend"
    SCREEN = "screen"


class ResolutionState(StrEnum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    MISSING = "missing"
    CIRCULAR = "circular"
    EXTERNAL = "external"


@dataclass(frozen=True)
class ContractReference(Generic[T]):
    """Shared non-recursively-expanding reference shape."""

    ref: str
    kind: ReferenceKind = ReferenceKind.UNKNOWN
    name: str | None = None
    owner: str | None = None
    state: ResolutionState = ResolutionState.UNRESOLVED
    target: T | None = None
    source_path: str = ""
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def is_resolved(self) -> bool:
        return self.state == ResolutionState.RESOLVED and self.target is not None


class SchemaUseKind(StrEnum):
    EMPTY = "empty"
    REFERENCE = "reference"
    MULTIPLE_REFERENCES = "multiple_references"
    INLINE = "inline"
    RESOLVED = "resolved"
    MIXED = "mixed"


@dataclass(frozen=True)
class SchemaUse(Generic[T]):
    """Shared schema-use shape for refs, inline schemas, and resolved targets."""

    kind: SchemaUseKind = SchemaUseKind.EMPTY
    ref: ContractReference[T] | None = None
    refs: tuple[ContractReference[T], ...] = ()
    schema: T | None = None
    inline: FrozenMap = field(default_factory=FrozenMap)
    source_path: str = ""
    diagnostics: tuple[ContractDiagnostic, ...] = ()

    @property
    def is_reference(self) -> bool:
        return self.kind in {
            SchemaUseKind.REFERENCE,
            SchemaUseKind.MULTIPLE_REFERENCES,
            SchemaUseKind.MIXED,
        }

    @property
    def is_inline(self) -> bool:
        return bool(self.inline)

    @property
    def is_resolved(self) -> bool:
        if self.schema is not None:
            return True
        references = self.refs or ((self.ref,) if self.ref is not None else ())
        return bool(references) and all(reference.is_resolved for reference in references)


@dataclass(frozen=True)
class CollectionCollision:
    """Duplicate id or name found while creating deterministic lookups."""

    lookup: str
    value: str
    indexes: tuple[int, ...]


@dataclass(frozen=True)
class ContractCollection(Generic[T]):
    """Ordered collection with deterministic id/name lookups and classifications."""

    all: tuple[T, ...] = ()
    by_id: Mapping[str, T] = field(default_factory=lambda: MappingProxyType({}))
    by_name: Mapping[str, T] = field(default_factory=lambda: MappingProxyType({}))
    classified: Mapping[str, tuple[T, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    collisions: tuple[CollectionCollision, ...] = ()

    @property
    def count(self) -> int:
        return len(self.all)

    def get(self, key: str) -> T | None:
        return self.by_id.get(key) or self.by_name.get(key)

    def group(self, name: str) -> tuple[T, ...]:
        return self.classified.get(name, ())


@dataclass(frozen=True)
class StructuredNotes:
    """Known information-note categories plus unknown named categories."""

    explain: tuple[str, ...] = ()
    access: tuple[str, ...] = ()
    implement: tuple[str, ...] = ()
    validation: tuple[str, ...] = ()
    security: tuple[str, ...] = ()
    observability: tuple[str, ...] = ()
    ux: tuple[str, ...] = ()
    performance: tuple[str, ...] = ()
    testing: tuple[str, ...] = ()
    other: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class SourceObject:
    """Immutable raw/extensions/diagnostics attached to one normalized object."""

    raw: FrozenMap = field(default_factory=FrozenMap)
    extensions: FrozenMap = field(default_factory=FrozenMap)
    diagnostics: tuple[ContractDiagnostic, ...] = ()
    source_path: str = ""

    @property
    def loss_count(self) -> int:
        return sum(
            1
            for diagnostic in self.diagnostics
            if diagnostic.category == DiagnosticCategory.LOST
        )


def presence_from_mapping(
    source: Mapping[str, Any],
    key: str,
    *,
    source_path: str = "",
) -> PresenceValue[Any]:
    """Preserve key presence separately from its value."""

    path = f"{source_path}.{key}" if source_path else key
    if key not in source:
        return PresenceValue.missing(source_path=path)
    return PresenceValue.authored(source[key], source_path=path)


def source_object(
    raw: Mapping[str, Any] | None,
    *,
    source_path: str = "",
    known_keys: Iterable[str] = (),
    diagnostics: Iterable[ContractDiagnostic] = (),
) -> SourceObject:
    """Freeze source data and retain unknown x-* extensions and diagnostics."""

    values = raw or {}
    extensions = {
        str(key): value
        for key, value in values.items()
        if isinstance(key, str) and key.startswith("x-")
    }
    known = set(known_keys)
    generated_diagnostics = list(diagnostics)
    for key, value in values.items():
        if key in known or (isinstance(key, str) and key.startswith("x-")):
            continue
        generated_diagnostics.append(
            ContractDiagnostic(
                category=DiagnosticCategory.RAW_ONLY,
                message=f"Source key is preserved raw but not normalized: {key}",
                source_path=f"{source_path}.{key}" if source_path else str(key),
                level=DiagnosticLevel.INFO,
                value=freeze_source_value(value),
            )
        )
    return SourceObject(
        raw=freeze_source_map(values),
        extensions=freeze_source_map(extensions),
        diagnostics=tuple(generated_diagnostics),
        source_path=source_path,
    )


def contract_collection(
    items: Iterable[T],
    *,
    id_of: Callable[[T], str | None] = lambda item: getattr(item, "id", None),
    name_of: Callable[[T], str | None] = lambda item: _name_value(
        getattr(item, "name", None)
    ),
    classifiers: Mapping[str, Callable[[T], bool]] | None = None,
) -> ContractCollection[T]:
    """Build ordered immutable lookup and classification views."""

    ordered = tuple(items)
    by_id, id_collisions = _lookup(ordered, id_of, lookup="id")
    by_name, name_collisions = _lookup(ordered, name_of, lookup="name")
    classified = {
        name: tuple(item for item in ordered if predicate(item))
        for name, predicate in (classifiers or {}).items()
    }
    return ContractCollection(
        all=ordered,
        by_id=MappingProxyType(by_id),
        by_name=MappingProxyType(by_name),
        classified=MappingProxyType(classified),
        collisions=(*id_collisions, *name_collisions),
    )


def structured_notes(value: Any) -> StructuredNotes:
    """Normalize strings, lists, and named note categories without loss."""

    if value is None:
        return StructuredNotes()
    if isinstance(value, str | list | tuple):
        return StructuredNotes(explain=_note_values(value))
    if not isinstance(value, Mapping):
        return StructuredNotes(other=MappingProxyType({"unknown": (str(value),)}))

    known: dict[str, tuple[str, ...]] = {}
    other: dict[str, tuple[str, ...]] = {}
    aliases = {
        "explain": "explain",
        "access": "access",
        "implement": "implement",
        "implementation": "implement",
        "validation": "validation",
        "security": "security",
        "observability": "observability",
        "ux": "ux",
        "user_experience": "ux",
        "performance": "performance",
        "testing": "testing",
        "test": "testing",
    }
    for raw_name, raw_value in value.items():
        name = str(raw_name)
        normalized = name.lower().replace("-", "_").replace(" ", "_")
        target = aliases.get(normalized)
        if target is None:
            other[name] = _note_values(raw_value)
        else:
            known[target] = _note_values(raw_value)
    return StructuredNotes(
        explain=known.get("explain", ()),
        access=known.get("access", ()),
        implement=known.get("implement", ()),
        validation=known.get("validation", ()),
        security=known.get("security", ()),
        observability=known.get("observability", ()),
        ux=known.get("ux", ()),
        performance=known.get("performance", ()),
        testing=known.get("testing", ()),
        other=MappingProxyType(other),
    )


def _lookup(
    items: tuple[T, ...],
    value_of: Callable[[T], str | None],
    *,
    lookup: str,
) -> tuple[dict[str, T], tuple[CollectionCollision, ...]]:
    indexes: dict[str, list[int]] = {}
    result: dict[str, T] = {}
    for index, item in enumerate(items):
        value = value_of(item)
        if not value:
            continue
        indexes.setdefault(value, []).append(index)
        result.setdefault(value, item)
    collisions = tuple(
        CollectionCollision(lookup=lookup, value=value, indexes=tuple(positions))
        for value, positions in sorted(indexes.items())
        if len(positions) > 1
    )
    return result, collisions


def _name_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    for attribute in ("raw", "clean", "original"):
        candidate = getattr(value, attribute, None)
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def _note_values(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value)
    return (str(value),)
