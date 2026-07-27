from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from codepotg.diagnostics import SourceIdentity, SourceSpan

from ..loading.source import LoadedSource


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    source: LoadedSource
    identity: SourceIdentity
    value: dict[str, object]
    spans: Mapping[str, SourceSpan]
    openapi_version: str

    @classmethod
    def create(
        cls,
        *,
        source: LoadedSource,
        value: dict[str, object],
        spans: dict[str, SourceSpan],
        openapi_version: str,
    ) -> ParsedDocument:
        return cls(
            source=source,
            identity=source.identity,
            value=value,
            spans=MappingProxyType(dict(spans)),
            openapi_version=openapi_version,
        )

    def span(self, pointer: str) -> SourceSpan | None:
        current = pointer
        while True:
            span = self.spans.get(current)
            if span is not None:
                return span
            if not current:
                return None
            current = current.rsplit("/", 1)[0]
