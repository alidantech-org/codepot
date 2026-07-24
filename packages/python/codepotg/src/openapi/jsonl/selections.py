from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import JsonlLookupError, JsonlSelectionError
from .hot_index import BoundedHotIndex, HotIndexStats
from .models import HotIndexLimits, RecordLocation
from .store import JsonlIndexStore


class SelectionClass(StrEnum):
    """Known source-data classes available to template planning."""

    SCHEMAS = "schemas"
    MODELS = "models"
    DTOS = "dtos"
    ENUMS = "enums"
    PRIMITIVES = "primitives"
    ENTITIES = "entities"
    OPERATIONS = "operations"
    PATHS = "paths"
    RESOURCES = "resources"
    ACCESS = "access"
    FRONTENDS = "frontends"
    BASE_ENTITIES = "base_entities"
    PARAMETERS = "parameters"
    REQUEST_BODIES = "request_bodies"
    RESPONSES = "responses"
    SECURITY_SCHEMES = "security_schemes"


class SelectionScope(StrEnum):
    """How selected source records are grouped for one emission."""

    EACH = "each"
    ALL = "all"
    RESOURCE = "resource"


@dataclass(frozen=True, slots=True)
class SelectionDefinition:
    """One canonical selection and its JSONL/index routing facts."""

    id: str
    selection_class: SelectionClass
    section: str
    kinds: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SelectionHandle:
    """Small source-location fact used before raw context is loaded."""

    selection: str
    key: str
    ref: str | None
    kind: str | None
    resources: tuple[str, ...]
    location: RecordLocation

    @property
    def cache_key(self) -> str:
        pointer = self.location.pointer or ""
        return (
            f"{self.location.file}:{self.location.offset}:"
            f"{self.location.length}:{pointer}"
        )


@dataclass(frozen=True, slots=True)
class SelectionRecord:
    """One lazily loaded raw record shared by all emissions for that source."""

    handle: SelectionHandle
    raw: Any

    @property
    def key(self) -> str:
        return self.handle.key

    @property
    def ref(self) -> str | None:
        return self.handle.ref

    @property
    def kind(self) -> str | None:
        return self.handle.kind

    @property
    def resources(self) -> tuple[str, ...]:
        return self.handle.resources


@dataclass(frozen=True, slots=True)
class SelectionGroup:
    """Lightweight grouping of source handles for aggregate emissions."""

    selection: str
    scope: SelectionScope
    key: str
    handles: tuple[SelectionHandle, ...]
    resource: str | None = None

    @property
    def count(self) -> int:
        return len(self.handles)


class SelectionCatalog:
    """Validated registry of every supported canonical selection."""

    def __init__(self, definitions: Sequence[SelectionDefinition]) -> None:
        by_id: dict[str, SelectionDefinition] = {}
        aliases: dict[str, str] = {}

        for definition in definitions:
            if not definition.id:
                raise JsonlSelectionError("Selection ids must be non-empty")
            if definition.id in by_id or definition.id in aliases:
                raise JsonlSelectionError(f"Duplicate selection id: {definition.id}")
            by_id[definition.id] = definition

            for alias in definition.aliases:
                if not alias:
                    raise JsonlSelectionError(
                        f"Selection '{definition.id}' contains an empty alias"
                    )
                if alias in by_id or alias in aliases:
                    raise JsonlSelectionError(f"Duplicate selection alias: {alias}")
                aliases[alias] = definition.id

        self._by_id = by_id
        self._aliases = aliases

    def resolve(self, selection: str) -> SelectionDefinition:
        canonical = self._aliases.get(selection, selection)
        definition = self._by_id.get(canonical)
        if definition is None:
            available = ", ".join(sorted(self._by_id))
            raise JsonlSelectionError(
                f"Unknown JSONL selection '{selection}'. Available: {available}."
            )
        return definition

    def definitions(self) -> tuple[SelectionDefinition, ...]:
        return tuple(self._by_id[key] for key in sorted(self._by_id))


DEFAULT_SELECTION_CATALOG = SelectionCatalog(
    (
        SelectionDefinition(
            id="schemas.all",
            selection_class=SelectionClass.SCHEMAS,
            section="components/schemas",
            aliases=("schemas",),
        ),
        SelectionDefinition(
            id="schemas.emit_models",
            selection_class=SelectionClass.MODELS,
            section="components/schemas",
            kinds=("model",),
            aliases=("models",),
        ),
        SelectionDefinition(
            id="schemas.emit_dtos",
            selection_class=SelectionClass.DTOS,
            section="components/schemas",
            kinds=("dto", "query", "params", "body", "request", "response"),
            aliases=("dtos",),
        ),
        SelectionDefinition(
            id="schemas.emit_enums",
            selection_class=SelectionClass.ENUMS,
            section="components/schemas",
            kinds=("enum",),
            aliases=("enums",),
        ),
        SelectionDefinition(
            id="schemas.primitives",
            selection_class=SelectionClass.PRIMITIVES,
            section="components/schemas",
            kinds=("primitive", "string", "integer", "number", "boolean", "array", "null"),
            aliases=("primitives",),
        ),
        SelectionDefinition(
            id="entities",
            selection_class=SelectionClass.ENTITIES,
            section="x-codegen/entities",
        ),
        SelectionDefinition(
            id="operations",
            selection_class=SelectionClass.OPERATIONS,
            section="paths",
            kinds=("operation",),
        ),
        SelectionDefinition(
            id="paths",
            selection_class=SelectionClass.PATHS,
            section="paths",
            kinds=("path",),
        ),
        SelectionDefinition(
            id="resources",
            selection_class=SelectionClass.RESOURCES,
            section="x-codegen/resources",
        ),
        SelectionDefinition(
            id="access",
            selection_class=SelectionClass.ACCESS,
            section="x-codegen/access",
        ),
        SelectionDefinition(
            id="frontends",
            selection_class=SelectionClass.FRONTENDS,
            section="x-codegen/frontends",
        ),
        SelectionDefinition(
            id="base_entities",
            selection_class=SelectionClass.BASE_ENTITIES,
            section="x-codegen/baseEntities",
            aliases=("baseEntities",),
        ),
        SelectionDefinition(
            id="components.parameters",
            selection_class=SelectionClass.PARAMETERS,
            section="components/parameters",
            aliases=("parameters",),
        ),
        SelectionDefinition(
            id="components.request_bodies",
            selection_class=SelectionClass.REQUEST_BODIES,
            section="components/requestBodies",
            aliases=("requestBodies",),
        ),
        SelectionDefinition(
            id="components.responses",
            selection_class=SelectionClass.RESPONSES,
            section="components/responses",
            aliases=("responses",),
        ),
        SelectionDefinition(
            id="components.security_schemes",
            selection_class=SelectionClass.SECURITY_SCHEMES,
            section="components/securitySchemes",
            aliases=("securitySchemes",),
        ),
    )
)


class JsonlSelectionStore:
    """JSONL-backed selectors with bounded raw-context reuse."""

    def __init__(
        self,
        cache_dir: str | Path,
        *,
        catalog: SelectionCatalog = DEFAULT_SELECTION_CATALOG,
        raw_cache_limits: HotIndexLimits | None = None,
        index_store: JsonlIndexStore | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.catalog = catalog
        self.index_store = index_store or JsonlIndexStore(self.cache_dir)
        self._sections = _load_sections(self.cache_dir)
        self._raw_cache: BoundedHotIndex[SelectionRecord] = BoundedHotIndex(
            raw_cache_limits or HotIndexLimits(max_entries=256, max_bytes=32 * 1024 * 1024),
            estimate=lambda key, value: len(key) + value.handle.location.length + 256,
        )
        self._loads = 0

    @property
    def load_count(self) -> int:
        return self._loads

    def raw_cache_stats(self) -> HotIndexStats:
        return self._raw_cache.stats()

    def iter_handles(
        self,
        selection: str,
        *,
        resource: str | None = None,
    ) -> Iterator[SelectionHandle]:
        definition = self.catalog.resolve(selection)
        canonical = definition.id

        if resource is not None:
            yield from self._iter_resource_handles(definition, canonical, resource)
            return

        if definition.kinds:
            yield from self._iter_kind_handles(definition, canonical)
            return

        yield from self._iter_section_handles(definition, canonical)

    def groups(
        self,
        selection: str,
        *,
        scope: SelectionScope = SelectionScope.EACH,
        resource: str | None = None,
    ) -> Iterator[SelectionGroup]:
        definition = self.catalog.resolve(selection)
        canonical = definition.id

        if scope == SelectionScope.EACH:
            for handle in self.iter_handles(canonical, resource=resource):
                yield SelectionGroup(
                    selection=canonical,
                    scope=scope,
                    key=handle.key,
                    handles=(handle,),
                    resource=resource,
                )
            return

        if scope == SelectionScope.ALL:
            handles = tuple(self.iter_handles(canonical, resource=resource))
            if handles:
                yield SelectionGroup(
                    selection=canonical,
                    scope=scope,
                    key=f"selection:{canonical}:all",
                    handles=handles,
                    resource=resource,
                )
            return

        if scope != SelectionScope.RESOURCE:
            raise JsonlSelectionError(f"Unsupported selection scope: {scope}")

        resources = (resource,) if resource is not None else self.resource_names()
        for resource_name in resources:
            handles = tuple(self.iter_handles(canonical, resource=resource_name))
            if not handles:
                continue
            yield SelectionGroup(
                selection=canonical,
                scope=scope,
                key=f"selection:{canonical}:resource:{resource_name}",
                handles=handles,
                resource=resource_name,
            )

    def resource_names(self) -> tuple[str, ...]:
        names = [handle.key.split(":", 1)[1] for handle in self.iter_handles("resources")]
        return tuple(sorted(set(names)))

    def load(self, handle: SelectionHandle) -> SelectionRecord:
        cached = self._raw_cache.get(handle.cache_key)
        if cached is not None:
            return cached

        raw = self.index_store.read_location(handle.location)
        record = SelectionRecord(handle=handle, raw=raw)
        self._loads += 1
        self._raw_cache.put(handle.cache_key, record)
        return record

    def load_group(self, group: SelectionGroup) -> Iterator[SelectionRecord]:
        for handle in group.handles:
            yield self.load(handle)

    def _iter_kind_handles(
        self,
        definition: SelectionDefinition,
        canonical: str,
    ) -> Iterator[SelectionHandle]:
        locations: dict[str, RecordLocation] = {}
        for kind in definition.kinds:
            for fact in self.index_store.find_mentions("kind", kind):
                item = fact.get("item")
                if not isinstance(item, str) or item in locations:
                    continue
                location = self.index_store.get_by_key(item)
                if location is None or not _matches_definition(location, definition):
                    continue
                locations[item] = location

        for key in sorted(locations):
            yield _handle(canonical, locations[key])

    def _iter_resource_handles(
        self,
        definition: SelectionDefinition,
        canonical: str,
        resource: str,
    ) -> Iterator[SelectionHandle]:
        locations: dict[str, RecordLocation] = {}
        for fact in self.index_store.find_mentions("resource", resource):
            item = fact.get("item")
            if not isinstance(item, str) or item in locations:
                continue
            location = self.index_store.get_by_key(item)
            if location is None or not _matches_definition(location, definition):
                continue
            locations[item] = location

        for key in sorted(locations):
            location = locations[key]
            resources = tuple(sorted(set((*location.resources, resource))))
            yield _handle(canonical, location, resources=resources)

    def _iter_section_handles(
        self,
        definition: SelectionDefinition,
        canonical: str,
    ) -> Iterator[SelectionHandle]:
        relative = self._sections.get(definition.section)
        if relative is None:
            return
        path = _cache_file(self.cache_dir, relative)
        try:
            with path.open("rb") as stream:
                while raw_line := stream.readline():
                    offset = stream.tell() - len(raw_line)
                    line = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
                    try:
                        envelope = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise JsonlLookupError(f"Invalid section JSONL line in {path}") from exc
                    if not isinstance(envelope, Mapping):
                        raise JsonlLookupError(f"Invalid section JSONL envelope in {path}")
                    location = _location_from_envelope(
                        definition.section,
                        relative,
                        offset,
                        line,
                        envelope,
                    )
                    if _matches_definition(location, definition):
                        yield _handle(canonical, location)
        except OSError as exc:
            raise JsonlLookupError(f"Unable to stream JSONL section: {path}") from exc


def _handle(
    selection: str,
    location: RecordLocation,
    *,
    resources: tuple[str, ...] | None = None,
) -> SelectionHandle:
    return SelectionHandle(
        selection=selection,
        key=location.key,
        ref=location.ref,
        kind=location.kind,
        resources=location.resources if resources is None else resources,
        location=location,
    )


def _matches_definition(
    location: RecordLocation,
    definition: SelectionDefinition,
) -> bool:
    if location.section != definition.section:
        return False
    if definition.kinds and location.kind not in definition.kinds:
        return False
    return True


def _location_from_envelope(
    section: str,
    relative: str,
    offset: int,
    line: bytes,
    envelope: Mapping[str, Any],
) -> RecordLocation:
    key = envelope.get("key")
    if not isinstance(key, str) or not key:
        raise JsonlLookupError(f"Section record is missing a stable key: {relative}@{offset}")
    ref = envelope.get("ref")
    kind = envelope.get("kind")
    raw_resources = envelope.get("resources", ())
    if not isinstance(raw_resources, list | tuple):
        raise JsonlLookupError(f"Section record has invalid resources: {relative}@{offset}")
    return RecordLocation(
        section=section,
        file=relative,
        offset=offset,
        length=len(line),
        sha256=f"sha256:{hashlib.sha256(line).hexdigest()}",
        key=key,
        ref=str(ref) if ref is not None else None,
        kind=str(kind) if kind is not None else None,
        resources=tuple(str(item) for item in raw_resources),
    )


def _load_sections(cache_dir: Path) -> dict[str, str]:
    path = cache_dir / "manifest.json"
    try:
        manifest = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise JsonlLookupError(f"Unable to load JSONL manifest: {path}") from exc
    if not isinstance(manifest, Mapping):
        raise JsonlLookupError(f"Invalid JSONL manifest: {path}")
    sections = manifest.get("sections")
    if not isinstance(sections, Mapping):
        raise JsonlLookupError(f"JSONL manifest has no sections: {path}")

    result: dict[str, str] = {}
    for name, raw in sections.items():
        if not isinstance(name, str) or not isinstance(raw, Mapping):
            continue
        relative = raw.get("file")
        if isinstance(relative, str):
            _cache_file(cache_dir, relative)
            result[name] = relative
    return result


def _cache_file(root: Path, relative: str) -> Path:
    if "\\" in relative:
        raise JsonlLookupError(f"Indexed cache path is not normalized: {relative}")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise JsonlLookupError(f"Indexed cache path is unsafe: {relative}")
    return root / Path(*pure.parts)
