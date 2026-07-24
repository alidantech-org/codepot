from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TypeAlias

from openapi.jsonl.selections import (
    JsonlSelectionStore,
    SelectionGroup,
    SelectionRecord,
    SelectionScope,
)

from .virtual_outputs import VirtualOutput, VirtualOutputRegistry

SelectionContext: TypeAlias = SelectionRecord | SelectionGroup
OutputPathResolver: TypeAlias = Callable[[SelectionContext], str | Path | PurePosixPath]
SymbolResolver: TypeAlias = Callable[[SelectionContext], Sequence[str]]


@dataclass(frozen=True, slots=True)
class SelectionEmission:
    """One internal template emission consuming a canonical selection."""

    id: str
    template_path: str | Path | PurePosixPath
    output_path: OutputPathResolver
    symbols: SymbolResolver | None = None


@dataclass(frozen=True, slots=True)
class SelectionPlan:
    """Deterministic result of lazy source selection and virtual path planning."""

    selection: str
    scope: SelectionScope
    groups: tuple[SelectionGroup, ...]
    outputs: tuple[VirtualOutput, ...]
    records_loaded: int = 0


class JsonlSelectionPlanner:
    """Plan outputs from JSONL selections without requiring generated files."""

    def __init__(
        self,
        store: JsonlSelectionStore,
        *,
        registry: VirtualOutputRegistry | None = None,
    ) -> None:
        self.store = store
        self.registry = registry if registry is not None else VirtualOutputRegistry()

    def plan(
        self,
        selection: str,
        emissions: Sequence[SelectionEmission],
        *,
        scope: SelectionScope = SelectionScope.EACH,
        resource: str | None = None,
    ) -> SelectionPlan:
        definition = self.store.catalog.resolve(selection)
        canonical = definition.id
        _validate_emissions(emissions)

        before_loads = self.store.load_count
        groups: list[SelectionGroup] = []
        outputs: list[VirtualOutput] = []

        for group in self.store.groups(canonical, scope=scope, resource=resource):
            groups.append(group)
            context: SelectionContext
            source_ref: str | None
            source_key: str
            output_resource = group.resource

            if scope == SelectionScope.EACH:
                record = self.store.load(group.handles[0])
                context = record
                source_ref = record.ref
                source_key = record.key
                if output_resource is None and len(record.resources) == 1:
                    output_resource = record.resources[0]
            else:
                context = group
                source_ref = None
                source_key = group.key

            for emission in emissions:
                symbols = (
                    tuple(emission.symbols(context))
                    if emission.symbols is not None
                    else ()
                )
                outputs.append(
                    self.registry.register(
                        selection=canonical,
                        emission=emission.id,
                        source_key=source_key,
                        source_ref=source_ref,
                        template_path=emission.template_path,
                        output_path=emission.output_path(context),
                        symbols=symbols,
                        resource=output_resource,
                    )
                )

        return SelectionPlan(
            selection=canonical,
            scope=scope,
            groups=tuple(groups),
            outputs=tuple(outputs),
            records_loaded=self.store.load_count - before_loads,
        )

    def records_for_group(self, group: SelectionGroup) -> Iterator[SelectionRecord]:
        """Load aggregate render contexts lazily when a template actually needs them."""

        return self.store.load_group(group)


def _validate_emissions(emissions: Sequence[SelectionEmission]) -> None:
    if not emissions:
        raise ValueError("At least one selection emission is required")
    seen: set[str] = set()
    for emission in emissions:
        if not emission.id:
            raise ValueError("Selection emission ids must be non-empty")
        if emission.id in seen:
            raise ValueError(f"Duplicate selection emission id: {emission.id}")
        seen.add(emission.id)
