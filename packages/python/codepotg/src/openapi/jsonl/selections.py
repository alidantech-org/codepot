from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .errors import JsonlSelectionError
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
            kinds=(
                "primitive",
                "string",
                "integer",
                "number",
                "boolean",
                "array",
                "null",
            ),
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
    """SQLite-planned selectors with exact lazy JSONL raw loads."""

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
        limits = raw_cache_limits or HotIndexLimits(
            max_entries=256,
            max_bytes=32 * 1024 * 1024,
        )
        self._raw_cache: BoundedHotIndex[SelectionRecord] = BoundedHotIndex(
            limits,
            estimate=lambda key, value: len(key) + value.handle.location.length + 256,
        )
        self._loads = 0
        self._closed = False

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
        mention = ("resource", resource) if resource is not None else None
        for location in self.index_store.iter_locations(
            definition.section,
            kinds=definition.kinds,
            mention=mention,
        ):
            resources = location.resources
            if resource is not None and resource not in resources:
                resources = tuple(sorted({*resources, resource}))
            yield _handle(canonical, location, resources=resources)

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
        names = {
            str(fact["value"])
            for fact in self.index_store.iter_mentions("resource")
            if isinstance(fact.get("value"), str) and fact.get("value")
        }
        if not names:
            names.update(
                handle.key.split(":", 1)[1]
                for handle in self.iter_handles("resources")
                if ":" in handle.key
            )
        return tuple(sorted(names))

    def load(self, handle: SelectionHandle) -> SelectionRecord:
        cached = self._raw_cache.get(handle.cache_key)
        if cached is not None:
            return cached

        raw = self.index_store.read_location(handle.location, verify=False)
        record = SelectionRecord(handle=handle, raw=raw)
        self._loads += 1
        self._raw_cache.put(handle.cache_key, record)
        return record

    def load_group(self, group: SelectionGroup) -> Iterator[SelectionRecord]:
        for handle in group.handles:
            yield self.load(handle)

    def close(self) -> None:
        if self._closed:
            return
        self.index_store.close()
        self._closed = True


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
