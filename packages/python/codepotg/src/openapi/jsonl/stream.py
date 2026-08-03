from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import ijson

from .errors import JsonlInputError, JsonlLimitError
from .models import ExtractedRecord, JsonlLimits, StreamSummary

_COMPONENT_COLLECTIONS = frozenset(
    {
        "schemas",
        "parameters",
        "requestBodies",
        "responses",
        "securitySchemes",
        "headers",
        "examples",
        "links",
        "callbacks",
        "pathItems",
    }
)
_X_CODEGEN_COLLECTIONS = frozenset(
    {"resources", "frontends", "access", "baseEntities", "entities"}
)
_ROOT_METADATA_KEYS = frozenset({"openapi", "info", "security", "servers"})
_SIMPLE_EVENTS = frozenset({"null", "boolean", "integer", "double", "number", "string"})


class _ValueBudget:
    __slots__ = ("items", "bytes", "max_items", "max_bytes", "max_depth")

    def __init__(self, *, max_items: int, max_bytes: int, max_depth: int) -> None:
        self.items = 0
        self.bytes = 0
        self.max_items = max_items
        self.max_bytes = max_bytes
        self.max_depth = max_depth

    def add(self, value: Any, depth: int) -> None:
        if depth > self.max_depth:
            raise JsonlLimitError(f"JSON value exceeds maximum depth {self.max_depth}")
        self.items += 1
        if self.items > self.max_items:
            raise JsonlLimitError(f"JSON value exceeds maximum item count {self.max_items}")
        if isinstance(value, str):
            self.bytes += len(value.encode("utf-8"))
        elif isinstance(value, bytes | bytearray):
            self.bytes += len(value)
        else:
            self.bytes += 16
        if self.bytes > self.max_bytes:
            raise JsonlLimitError(f"JSON value exceeds approximate byte limit {self.max_bytes}")


def stream_openapi_json(
    source: str | Path,
    *,
    on_record: Callable[[ExtractedRecord], None],
    limits: JsonlLimits | None = None,
) -> StreamSummary:
    """Stream one OpenAPI JSON document and emit direct section records.

    Only one direct path/component/x-codegen item is constructed at a time.
    Root metadata and root ``x-*`` extensions remain bounded in the manifest.
    Unknown unsupported collections are skipped event-by-event.
    """
    source_path = Path(source)
    if source_path.suffix.lower() != ".json":
        raise JsonlInputError("JSONL compilation currently requires an OpenAPI .json input")
    if not source_path.exists():
        raise JsonlInputError(f"OpenAPI input does not exist: {source_path}")
    if not source_path.is_file():
        raise JsonlInputError(f"OpenAPI input is not a file: {source_path}")

    resolved_limits = limits or JsonlLimits()
    root: dict[str, Any] = {}
    saw_paths = False

    with source_path.open("rb") as stream:
        events = iter(ijson.basic_parse(stream, use_float=True))
        first_event, _ = _next_event(events)
        if first_event != "start_map":
            raise JsonlInputError("OpenAPI JSON root must be an object")

        while True:
            event, value = _next_event(events)
            if event == "end_map":
                break
            if event != "map_key":
                raise JsonlInputError(f"Expected root object key, received {event}")
            root_key = str(value)
            value_event, value_token = _next_event(events)

            if root_key in _ROOT_METADATA_KEYS or (
                root_key.startswith("x-") and root_key != "x-codegen"
            ):
                budget = _ValueBudget(
                    max_items=resolved_limits.max_root_items,
                    max_bytes=resolved_limits.max_root_bytes,
                    max_depth=resolved_limits.max_depth,
                )
                root[root_key] = _read_value(
                    events,
                    value_event,
                    value_token,
                    budget=budget,
                    depth=0,
                )
            elif root_key == "paths":
                saw_paths = True
                _stream_direct_mapping(
                    events,
                    value_event,
                    value_token,
                    section="paths",
                    on_record=on_record,
                    limits=resolved_limits,
                )
            elif root_key == "components":
                _stream_collection_group(
                    events,
                    value_event,
                    value_token,
                    group="components",
                    supported=_COMPONENT_COLLECTIONS,
                    on_record=on_record,
                    limits=resolved_limits,
                )
            elif root_key == "x-codegen":
                _stream_collection_group(
                    events,
                    value_event,
                    value_token,
                    group="x-codegen",
                    supported=_X_CODEGEN_COLLECTIONS,
                    on_record=on_record,
                    limits=resolved_limits,
                )
            else:
                _skip_value(events, value_event)

    if "openapi" not in root:
        raise JsonlInputError("OpenAPI document is missing the 'openapi' field")
    if not saw_paths:
        raise JsonlInputError("OpenAPI document is missing the 'paths' field")

    return StreamSummary(root=root, source_size=source_path.stat().st_size)


def _stream_collection_group(
    events: Iterator[tuple[str, Any]],
    first_event: str,
    first_value: Any,
    *,
    group: str,
    supported: frozenset[str],
    on_record: Callable[[ExtractedRecord], None],
    limits: JsonlLimits,
) -> None:
    del first_value
    if first_event == "null":
        return
    if first_event != "start_map":
        raise JsonlInputError(f"OpenAPI '{group}' must be an object")

    while True:
        event, collection_name = _next_event(events)
        if event == "end_map":
            return
        if event != "map_key":
            raise JsonlInputError(f"Expected collection name in '{group}', received {event}")
        value_event, value_token = _next_event(events)
        collection = str(collection_name)
        if collection not in supported:
            _skip_value(events, value_event)
            continue
        _stream_direct_mapping(
            events,
            value_event,
            value_token,
            section=f"{group}/{collection}",
            on_record=on_record,
            limits=limits,
        )


def _stream_direct_mapping(
    events: Iterator[tuple[str, Any]],
    first_event: str,
    first_value: Any,
    *,
    section: str,
    on_record: Callable[[ExtractedRecord], None],
    limits: JsonlLimits,
) -> None:
    del first_value
    if first_event == "null":
        return
    if first_event != "start_map":
        raise JsonlInputError(f"OpenAPI section '{section}' must be an object")

    while True:
        event, name = _next_event(events)
        if event == "end_map":
            return
        if event != "map_key":
            raise JsonlInputError(f"Expected item name in '{section}', received {event}")
        value_event, value_token = _next_event(events)
        budget = _ValueBudget(
            max_items=limits.max_record_items,
            max_bytes=limits.max_record_bytes,
            max_depth=limits.max_depth,
        )
        raw = _read_value(events, value_event, value_token, budget=budget, depth=0)
        on_record(
            ExtractedRecord(
                section=section,
                name=str(name),
                raw=raw,
                estimated_bytes=max(1, budget.bytes),
            )
        )


def _read_value(
    events: Iterator[tuple[str, Any]],
    event: str,
    value: Any,
    *,
    budget: _ValueBudget,
    depth: int,
) -> Any:
    budget.add(value, depth)
    if event in _SIMPLE_EVENTS:
        return value
    if event == "start_map":
        result: dict[str, Any] = {}
        while True:
            child_event, child_value = _next_event(events)
            if child_event == "end_map":
                return result
            if child_event != "map_key":
                raise JsonlInputError(f"Expected object key, received {child_event}")
            key = str(child_value)
            budget.add(key, depth + 1)
            value_event, value_token = _next_event(events)
            result[key] = _read_value(
                events,
                value_event,
                value_token,
                budget=budget,
                depth=depth + 1,
            )
    if event == "start_array":
        result_list: list[Any] = []
        while True:
            child_event, child_value = _next_event(events)
            if child_event == "end_array":
                return result_list
            result_list.append(
                _read_value(
                    events,
                    child_event,
                    child_value,
                    budget=budget,
                    depth=depth + 1,
                )
            )
    raise JsonlInputError(f"Unsupported JSON parser event: {event}")


def _skip_value(events: Iterator[tuple[str, Any]], first_event: str) -> None:
    if first_event in _SIMPLE_EVENTS:
        return
    if first_event not in {"start_map", "start_array"}:
        raise JsonlInputError(f"Unsupported JSON parser event while skipping: {first_event}")
    depth = 1
    while depth:
        event, _ = _next_event(events)
        if event in {"start_map", "start_array"}:
            depth += 1
        elif event in {"end_map", "end_array"}:
            depth -= 1


def _next_event(events: Iterator[tuple[str, Any]]) -> tuple[str, Any]:
    try:
        return next(events)
    except StopIteration as exc:
        raise JsonlInputError("OpenAPI JSON ended unexpectedly") from exc
