from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from constants.openapi import (
    COMPONENTS,
    PARAMETERS,
    REQUEST_BODIES,
    RESPONSES,
    SCHEMAS,
    DEFAULT_TITLE,
    DESCRIPTION,
    INFO,
    OPENAPI,
    PATHS,
    SERVERS,
    TITLE,
    VERSION,
)

OpenApiDict = dict[str, Any]


@dataclass(frozen=True)
class OpenApiDocument:
    path: Path
    raw: OpenApiDict

    @property
    def openapi_version(self) -> str:
        return str(self.raw.get(OPENAPI, ""))

    @property
    def info(self) -> OpenApiDict:
        value = self.raw.get(INFO)
        return value if isinstance(value, dict) else {}

    @property
    def title(self) -> str:
        return str(self.info.get(TITLE, DEFAULT_TITLE))

    @property
    def description(self) -> str:
        return str(self.info.get(DESCRIPTION, ""))

    @property
    def api_version(self) -> str:
        return str(self.info.get(VERSION, ""))

    @property
    def paths(self) -> OpenApiDict:
        value = self.raw.get(PATHS)
        return value if isinstance(value, dict) else {}

    @property
    def servers(self) -> tuple[OpenApiDict, ...]:
        value = self.raw.get(SERVERS)
        if not isinstance(value, list):
            return ()

        return tuple(server for server in value if isinstance(server, dict))

    @property
    def components(self) -> OpenApiDict:
        value = self.raw.get(COMPONENTS)
        return value if isinstance(value, dict) else {}

    @property
    def schemas(self) -> OpenApiDict:
        value = self.components.get(SCHEMAS)
        return value if isinstance(value, dict) else {}

    @property
    def responses(self) -> OpenApiDict:
        value = self.components.get(RESPONSES)
        return value if isinstance(value, dict) else {}

    @property
    def request_bodies(self) -> OpenApiDict:
        value = self.components.get(REQUEST_BODIES)
        return value if isinstance(value, dict) else {}

    @property
    def parameters(self) -> OpenApiDict:
        value = self.components.get(PARAMETERS)
        return value if isinstance(value, dict) else {}
