from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .base import KernelData, SemanticId
from .naming import Name


class PresentationChannel(StrEnum):
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    COMMAND = "command"
    DOCUMENT = "document"
    CONVERSATIONAL = "conversational"


@dataclass(frozen=True, slots=True)
class PresentationEntry:
    id: SemanticId
    name: Name
    view: SemanticId
    address: str | None = None
    navigation_parent: SemanticId | None = None
    order: int = 0
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        if self.address is not None and (not self.address or self.address.strip() != self.address):
            raise ValueError("presentation entry addresses must be non-empty trimmed strings")
        if self.navigation_parent == self.id:
            raise ValueError("presentation entry cannot be its own navigation parent")


@dataclass(frozen=True, slots=True)
class Presentation:
    id: SemanticId
    name: Name
    channel: PresentationChannel
    entries: tuple[PresentationEntry, ...] = ()
    data: KernelData = field(default_factory=KernelData)

    def __post_init__(self) -> None:
        entry_ids = tuple(item.id for item in self.entries)
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("presentation entry ids must be unique")
        entry_names = tuple(item.name for item in self.entries)
        if len(entry_names) != len(set(entry_names)):
            raise ValueError("presentation entry names must be unique")
