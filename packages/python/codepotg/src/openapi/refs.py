from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from constants.openapi import COMPONENTS, COMPONENT_REF_PREFIX, JSON_POINTER_PREFIX, REF


@dataclass(frozen=True)
class OpenApiRef:
    raw: str
    parts: tuple[str, ...]

    @property
    def is_local(self) -> bool:
        return self.raw.startswith(JSON_POINTER_PREFIX)

    @property
    def is_component(self) -> bool:
        return self.raw.startswith(COMPONENT_REF_PREFIX)

    @property
    def section(self) -> str | None:
        if len(self.parts) >= 2 and self.parts[0] == COMPONENTS:
            return self.parts[1]
        return None

    @property
    def name(self) -> str | None:
        if len(self.parts) >= 3 and self.parts[0] == COMPONENTS:
            return self.parts[2]
        return None

    @property
    def component_key(self) -> tuple[str, str] | None:
        section = self.section
        name = self.name

        if section is None or name is None:
            return None

        return section, name


def parse_ref(value: str) -> OpenApiRef:
    if not value.startswith(JSON_POINTER_PREFIX):
        return OpenApiRef(raw=value, parts=())

    pointer = value.removeprefix(JSON_POINTER_PREFIX)
    parts = tuple(_decode_json_pointer_part(part) for part in pointer.split("/") if part)

    return OpenApiRef(raw=value, parts=parts)


def get_ref(node: Any) -> OpenApiRef | None:
    if not isinstance(node, dict):
        return None

    value = node.get(REF)

    if not isinstance(value, str) or not value:
        return None

    return parse_ref(value)


def find_refs(value: Any) -> tuple[OpenApiRef, ...]:
    refs: list[OpenApiRef] = []
    _walk_refs(value, refs)
    return tuple(refs)


def _walk_refs(value: Any, refs: list[OpenApiRef]) -> None:
    if isinstance(value, dict):
        ref = get_ref(value)
        if ref is not None:
            refs.append(ref)

        for child in value.values():
            _walk_refs(child, refs)

    elif isinstance(value, list):
        for child in value:
            _walk_refs(child, refs)


def _decode_json_pointer_part(value: str) -> str:
    return value.replace("~1", "/").replace("~0", "~")
