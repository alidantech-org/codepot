from __future__ import annotations

from collections.abc import Mapping

from jinja2 import BaseLoader, Environment, TemplateNotFound


class ImmutableRegistryLoader(BaseLoader):
    """Loader limited to one immutable request-owned template registry."""

    def __init__(self, sources: Mapping[str, str]) -> None:
        self._sources = sources

    def get_source(
        self,
        environment: Environment,
        template: str,
    ) -> tuple[str, str, object | None]:
        del environment
        try:
            source = self._sources[template]
        except KeyError as exc:
            raise TemplateNotFound(template) from exc
        return source, template, None
