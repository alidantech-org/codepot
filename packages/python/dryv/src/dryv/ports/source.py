from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from dryv.api import CancellationToken
from dryv.diagnostics import Diagnostics
from dryv.domain.ir import Contract, FrozenObject
from dryv.plugins import PluginDescriptor


@dataclass(frozen=True, slots=True)
class SourceAdapterRequest:
    source_id: str
    location: str | None = None
    content: str | bytes | None = None
    options: FrozenObject = ()

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("source adapter requests require source_id")
        if (self.location is None) == (self.content is None):
            raise ValueError("source adapter requests require exactly one location or content")


@dataclass(frozen=True, slots=True)
class SourceAdapterResult:
    contract: Contract | None
    digest: str | None
    diagnostics: Diagnostics = Diagnostics()

    def __post_init__(self) -> None:
        if self.contract is not None and not self.digest:
            raise ValueError("successful source results require a stable digest")
        if self.contract is None and not self.diagnostics.has_errors:
            raise ValueError("missing source contract requires an error diagnostic")


@runtime_checkable
class SourceAdapter(Protocol):
    @property
    def plugin(self) -> PluginDescriptor: ...

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult: ...
