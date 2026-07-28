from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

_HELPER_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_HELPER_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class HelperKind(StrEnum):
    FILTER = "filter"
    TEST = "test"
    GLOBAL = "global"


@dataclass(frozen=True, slots=True)
class HelperDescriptor:
    id: str
    name: str
    kind: HelperKind
    version: str
    implementation: Callable[..., object]
    pure: bool = True
    documentation: str = ""

    def __post_init__(self) -> None:
        if _HELPER_ID.fullmatch(self.id) is None:
            raise ValueError(f"invalid helper id: {self.id!r}")
        if _HELPER_NAME.fullmatch(self.name) is None or self.name.startswith("_"):
            raise ValueError(f"invalid helper name: {self.name!r}")
        if not self.version or self.version.strip() != self.version:
            raise ValueError("helper version must be a non-empty trimmed string")
        if not callable(self.implementation):
            raise ValueError("helper implementation must be callable")
        if not self.pure:
            raise ValueError("registered Jinja helpers must declare pure deterministic behavior")

    def identity(self) -> tuple[str, str, str, str]:
        return (self.kind.value, self.id, self.name, self.version)
