from __future__ import annotations

from dataclasses import dataclass

from dryv_author.core import EventRef, OperationRef, PolicyRef, ViewRef, WorkflowRef


@dataclass(frozen=True, slots=True)
class PresentationEntryDeclaration:
    name: str
    view: ViewRef
    address: str | None = None
    navigation_parent: str | None = None
    order: int = 0
    policies: tuple[PolicyRef, ...] = ()
    operations: tuple[OperationRef[object, object], ...] = ()
    events: tuple[EventRef[object], ...] = ()
    workflows: tuple[WorkflowRef, ...] = ()

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("presentation entry name must be a non-empty trimmed string")
        if self.navigation_parent is not None and (
            not self.navigation_parent or self.navigation_parent.strip() != self.navigation_parent
        ):
            raise ValueError("presentation navigation parent must be a non-empty trimmed name")


@dataclass(frozen=True, slots=True)
class PresentationDeclaration:
    channel: str
    entries: tuple[PresentationEntryDeclaration, ...] = ()

    def __post_init__(self) -> None:
        if not self.channel or self.channel.strip() != self.channel:
            raise ValueError("presentation channel must be a non-empty trimmed string")
        names = tuple(item.name for item in self.entries)
        if len(names) != len(set(names)):
            raise ValueError("presentation entry names must be unique")
        known = set(names)
        parents = {item.name: item.navigation_parent for item in self.entries}
        for item in self.entries:
            parent = item.navigation_parent
            if parent is None:
                continue
            if parent not in known:
                raise ValueError(
                    f"presentation entry {item.name!r} references unknown navigation parent {parent!r}"
                )
            if parent == item.name:
                raise ValueError("presentation entry cannot be its own navigation parent")
        for name in names:
            seen: set[str] = set()
            current: str | None = name
            while current is not None:
                if current in seen:
                    raise ValueError("presentation navigation parents must not contain cycles")
                seen.add(current)
                current = parents[current]


__all__ = ["PresentationDeclaration", "PresentationEntryDeclaration"]
