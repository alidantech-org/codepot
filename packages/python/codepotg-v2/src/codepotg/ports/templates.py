from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from codepotg.api import CancellationToken
from codepotg.diagnostics import Diagnostics
from codepotg.plugins import PluginDescriptor


@dataclass(frozen=True, slots=True)
class RenderRequest:
    template_id: str
    source: str
    context: tuple[tuple[str, object], ...] = ()
    partials: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.template_id:
            raise ValueError("render requests require template_id")
        for label, values in (("render context", self.context), ("render partials", self.partials)):
            keys = tuple(key for key, _ in values)
            if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
                raise ValueError(f"{label} must be sorted by unique key")


@dataclass(frozen=True, slots=True)
class RenderResult:
    content: str | None
    diagnostics: Diagnostics = Diagnostics()

    def __post_init__(self) -> None:
        if self.content is None and not self.diagnostics.has_errors:
            raise ValueError("missing rendered content requires an error diagnostic")


@runtime_checkable
class TemplateEngine(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    @property
    def suffixes(self) -> tuple[str, ...]: ...

    def render(
        self,
        request: RenderRequest,
        cancellation: CancellationToken,
    ) -> RenderResult: ...
