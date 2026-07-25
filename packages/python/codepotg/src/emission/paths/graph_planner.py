from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from contracts.paths import (
    PathBarrel,
    PathConfig,
    PathEmission,
    PathLifecycleMode,
    PathSelection,
    PathSelectionScope,
)
from emission.planning import VirtualOutput, VirtualOutputRegistry
from emission.templates.path_expander import expand_template_path
from emission.templates.resolver import resolve_variable


class PathGraphPlanningError(ValueError):
    """Raised when a paths selection graph cannot be planned safely."""


@dataclass(frozen=True, slots=True)
class ResolvedSelectionContext:
    name: str
    select: str
    alias: str
    scope: str
    key: str
    item: Any | None
    items: tuple[Any, ...]
    resource: str | None

    @property
    def count(self) -> int:
        return len(self.items)


@dataclass(frozen=True, slots=True)
class ResolvedBarrelContext:
    name: str
    scope: str
    resource: str | None
    members: tuple[VirtualOutput, ...]
    symbols: tuple[str, ...]
    provides: tuple[str, ...]

    @property
    def count(self) -> int:
        return len(self.members)


@dataclass(frozen=True, slots=True)
class PathGraphFile:
    node_key: str
    selection: str
    source_key: str
    source_ref: str | None
    resource: str | None
    template_path: Path
    output_path: Path
    context: Mapping[str, Any]
    lifecycle: PathLifecycleMode
    provides: tuple[str, ...]
    provided_symbols: tuple[str, ...]
    providers: Mapping[str, str]
    depends_on: tuple[str, ...] = ()
    is_barrel: bool = False

    @property
    def identity(self) -> str:
        return f"{self.node_key}:{self.source_key}"


@dataclass(frozen=True, slots=True)
class PathGraphPlan:
    files: tuple[PathGraphFile, ...]
    registry: VirtualOutputRegistry


def plan_path_graph(
    *,
    config: PathConfig,
    base_context: Mapping[str, Any],
    template_root: Path,
    registry: VirtualOutputRegistry | None = None,
) -> PathGraphPlan:
    """Plan named selections, direct emissions, providers, and barrels."""

    output_registry = registry or VirtualOutputRegistry()
    if not config.uses_graph:
        return PathGraphPlan(files=(), registry=output_registry)

    selections = config.selection_by_name()
    groups = {
        name: _resolve_selection(selection, base_context)
        for name, selection in selections.items()
    }
    files = _direct_files(
        config,
        selections=selections,
        groups=groups,
        base_context=base_context,
        template_root=template_root,
        registry=output_registry,
    )
    effective_refs = {
        emission.name: frozenset(
            ref
            for output in output_registry.find_emission(emission.name)
            for ref in output.refs
        )
        for emission in config.emissions
    }
    effective_provides = {
        emission.name: frozenset(emission.provides)
        for emission in config.emissions
    }
    files.extend(
        _barrel_files(
            config,
            base_context=base_context,
            template_root=template_root,
            registry=output_registry,
            effective_refs=effective_refs,
            effective_provides=effective_provides,
        )
    )
    bound = _bind_exact_dependencies(
        files,
        config=config,
        registry=output_registry,
        effective_refs=effective_refs,
    )
    return PathGraphPlan(
        files=tuple(_topological_files(bound)),
        registry=output_registry,
    )


def _direct_files(
    config: PathConfig,
    *,
    selections: Mapping[str, PathSelection],
    groups: Mapping[str, tuple[ResolvedSelectionContext, ...]],
    base_context: Mapping[str, Any],
    template_root: Path,
    registry: VirtualOutputRegistry,
) -> list[PathGraphFile]:
    files: list[PathGraphFile] = []
    for emission in config.emissions:
        selection = selections[emission.selection]
        template_path = _require_template(template_root, emission.template)
        for selected in groups[selection.name]:
            context = _selection_context(
                base_context,
                selection,
                selected,
                emission,
            )
            output_path = _expand_output(config, emission.output, context)
            source_key, source_ref = _source_identity(selected)
            refs = _selected_refs(selected)
            symbols = _selected_symbols(selected)
            lifecycle = emission.lifecycle or config.write_policy.default_mode
            providers = {
                provider.purpose: provider.source
                for provider in emission.providers
            }
            registry.register(
                selection=selection.select,
                emission=emission.name,
                source_key=source_key,
                source_ref=source_ref,
                template_path=template_path.relative_to(template_root),
                output_path=output_path,
                refs=refs,
                symbols=symbols,
                provides=emission.provides,
                resource=selected.resource,
            )
            files.append(
                PathGraphFile(
                    node_key=emission.name,
                    selection=selection.name,
                    source_key=source_key,
                    source_ref=source_ref,
                    resource=selected.resource,
                    template_path=template_path.relative_to(template_root),
                    output_path=output_path,
                    context=context,
                    lifecycle=lifecycle,
                    provides=emission.provides,
                    provided_symbols=symbols,
                    providers=providers,
                )
            )
    return files


def _barrel_files(
    config: PathConfig,
    *,
    base_context: Mapping[str, Any],
    template_root: Path,
    registry: VirtualOutputRegistry,
    effective_refs: dict[str, frozenset[str]],
    effective_provides: dict[str, frozenset[str]],
) -> list[PathGraphFile]:
    files: list[PathGraphFile] = []
    for barrel in _ordered_barrels(config.barrels):
        template_path = _require_template(template_root, barrel.template)
        exported = barrel.exports
        resources = _barrel_resources(
            barrel,
            exported_nodes=exported,
            registry=registry,
        )
        for resource in resources:
            members = _barrel_members(
                barrel,
                exported_nodes=exported,
                registry=registry,
                resource=resource,
            )
            if not members:
                continue
            refs = tuple(sorted({ref for item in members for ref in item.refs}))
            symbols = tuple(
                sorted({symbol for item in members for symbol in item.symbols})
            )
            provides = tuple(
                sorted(
                    {
                        capability
                        for node in exported
                        for capability in effective_provides.get(
                            node,
                            frozenset(),
                        )
                    }
                )
            )
            barrel_context = ResolvedBarrelContext(
                name=barrel.name,
                scope=barrel.scope.value,
                resource=resource,
                members=members,
                symbols=symbols,
                provides=provides,
            )
            context = dict(base_context)
            context[barrel.alias] = barrel_context
            context["barrel"] = barrel_context
            context["providers"] = {}
            source_key = (
                f"barrel:{barrel.name}:resource:{resource}"
                if resource is not None
                else f"barrel:{barrel.name}:all"
            )
            output_path = _expand_output(config, barrel.output, context)
            registry.register(
                selection="barrels",
                emission=barrel.name,
                source_key=source_key,
                source_ref=None,
                template_path=template_path.relative_to(template_root),
                output_path=output_path,
                refs=refs,
                symbols=symbols,
                provides=provides,
                resource=resource,
            )
            files.append(
                PathGraphFile(
                    node_key=barrel.name,
                    selection="barrels",
                    source_key=source_key,
                    source_ref=None,
                    resource=resource,
                    template_path=template_path.relative_to(template_root),
                    output_path=output_path,
                    context=context,
                    lifecycle=(
                        barrel.lifecycle
                        or config.write_policy.default_mode
                    ),
                    provides=provides,
                    provided_symbols=symbols,
                    providers={},
                    depends_on=tuple(
                        item.output_path.as_posix() for item in members
                    ),
                    is_barrel=True,
                )
            )
        effective_refs[barrel.name] = frozenset(
            ref
            for node in exported
            for ref in effective_refs.get(node, frozenset())
        )
        effective_provides[barrel.name] = frozenset(
            capability
            for node in exported
            for capability in effective_provides.get(node, frozenset())
        )
    return files


def _resolve_selection(
    selection: PathSelection,
    base_context: Mapping[str, Any],
) -> tuple[ResolvedSelectionContext, ...]:
    value = resolve_variable(base_context, selection.select)
    items = _selection_items(value, owner=selection.name)
    if selection.scope == PathSelectionScope.EACH:
        return tuple(
            ResolvedSelectionContext(
                name=selection.name,
                select=selection.select,
                alias=selection.alias,
                scope=selection.scope.value,
                key=_item_key(item, index=index, selection=selection.name),
                item=item,
                items=(item,),
                resource=_resource_identity(item),
            )
            for index, item in enumerate(items)
        )
    if selection.scope == PathSelectionScope.ALL:
        return (
            ResolvedSelectionContext(
                name=selection.name,
                select=selection.select,
                alias=selection.alias,
                scope=selection.scope.value,
                key=f"selection:{selection.name}:all",
                item=None,
                items=items,
                resource=None,
            ),
        ) if items else ()

    grouped: dict[str, list[Any]] = defaultdict(list)
    for index, item in enumerate(items):
        resource = _resource_identity(item)
        if resource is None:
            key = _item_key(item, index=index, selection=selection.name)
            raise PathGraphPlanningError(
                f"Selection '{selection.name}' uses resource scope but item "
                f"'{key}' has no resource."
            )
        grouped[resource].append(item)
    return tuple(
        ResolvedSelectionContext(
            name=selection.name,
            select=selection.select,
            alias=selection.alias,
            scope=selection.scope.value,
            key=f"selection:{selection.name}:resource:{resource}",
            item=None,
            items=tuple(grouped[resource]),
            resource=resource,
        )
        for resource in sorted(grouped)
    )


def _selection_context(
    base_context: Mapping[str, Any],
    selection: PathSelection,
    selected: ResolvedSelectionContext,
    emission: PathEmission,
) -> dict[str, Any]:
    context = dict(base_context)
    context[selection.alias] = (
        selected.item if selected.item is not None else selected.items
    )
    context["selection"] = selected
    context["emission"] = emission
    context["providers"] = {
        provider.purpose: provider.source for provider in emission.providers
    }
    return context


def _selection_items(value: Any, *, owner: str) -> tuple[Any, ...]:
    if isinstance(value, Sequence) and not isinstance(
        value,
        str | bytes | bytearray,
    ):
        return tuple(value)
    raise PathGraphPlanningError(
        f"Selection '{owner}' must resolve to an ordered list or tuple, "
        f"got {type(value).__name__}."
    )


def _source_identity(
    selected: ResolvedSelectionContext,
) -> tuple[str, str | None]:
    if selected.item is None:
        return selected.key, None
    emit = getattr(selected.item, "emit", None)
    key = getattr(emit, "key", None) or selected.key
    ref = getattr(emit, "ref", None) or getattr(selected.item, "ref", None)
    return str(key), str(ref) if ref else None


def _selected_refs(selected: ResolvedSelectionContext) -> tuple[str, ...]:
    refs = {
        str(ref)
        for item in selected.items
        for ref in (
            getattr(getattr(item, "emit", None), "ref", None)
            or getattr(item, "ref", None),
        )
        if ref
    }
    return tuple(sorted(refs))


def _selected_symbols(selected: ResolvedSelectionContext) -> tuple[str, ...]:
    return tuple(
        sorted(
            symbol
            for symbol in {_symbol(item) for item in selected.items}
            if symbol
        )
    )


def _required_refs(selected: ResolvedSelectionContext) -> tuple[str, ...]:
    refs: set[str] = set()
    for item in selected.items:
        emit = getattr(item, "emit", None)
        for dependency in tuple(
            getattr(emit, "dependencies", ()) if emit is not None else ()
        ):
            if not getattr(dependency, "is_importable", False):
                continue
            ref = getattr(dependency, "ref", None)
            if isinstance(ref, str) and ref:
                refs.add(ref)
    return tuple(sorted(refs))


def _item_key(item: Any, *, index: int, selection: str) -> str:
    emit = getattr(item, "emit", None)
    key = getattr(emit, "key", None)
    if key:
        return str(key)
    identifier = getattr(item, "id", None)
    if identifier:
        return f"{selection}:{identifier}"
    name = _name_identity(getattr(item, "name", None))
    return f"{selection}:{name}" if name else f"{selection}:index:{index}"


def _resource_identity(item: Any) -> str | None:
    resource = _name_identity(getattr(item, "resource", None))
    if resource:
        return resource
    emit = getattr(item, "emit", None)
    path = tuple(
        getattr(emit, "resource_path", ()) if emit is not None else ()
    )
    return str(path[0]) if path else None


def _name_identity(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    identifier = getattr(value, "id", None)
    if isinstance(identifier, str) and identifier:
        return identifier
    nested = getattr(value, "name", None)
    if nested is not None and nested is not value:
        identity = _name_identity(nested)
        if identity:
            return identity
    for attribute in ("raw", "clean", "original"):
        candidate = getattr(value, attribute, None)
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def _symbol(item: Any) -> str | None:
    symbol = getattr(getattr(item, "lang", None), "symbol_name", None)
    if isinstance(symbol, str) and symbol and symbol != "-":
        return symbol
    return _name_identity(getattr(item, "name", None))


def _bind_exact_dependencies(
    files: list[PathGraphFile],
    *,
    config: PathConfig,
    registry: VirtualOutputRegistry,
    effective_refs: Mapping[str, frozenset[str]],
) -> list[PathGraphFile]:
    barrels = config.barrel_by_name()
    result: list[PathGraphFile] = []
    for file in files:
        if file.is_barrel:
            result.append(file)
            continue
        selected = file.context.get("selection")
        if not isinstance(selected, ResolvedSelectionContext):
            result.append(file)
            continue
        required = _required_refs(selected)
        if not required:
            result.append(file)
            continue
        sources = tuple(dict.fromkeys(file.providers.values()))
        if not sources:
            raise PathGraphPlanningError(
                f"Emission '{file.node_key}' requires imports {required} "
                "but declares no providers."
            )
        dependencies = set(file.depends_on)
        for ref in required:
            matching = tuple(
                source
                for source in sources
                if ref in effective_refs.get(source, frozenset())
            )
            if len(matching) > 1:
                raise PathGraphPlanningError(
                    f"Emission '{file.node_key}' has overlapping providers "
                    f"for '{ref}': {', '.join(matching)}"
                )
            if not matching:
                raise PathGraphPlanningError(
                    f"Emission '{file.node_key}' has no configured provider "
                    f"that emits '{ref}'."
                )
            source = matching[0]
            barrel = barrels.get(source)
            candidates = (
                registry.find_emission(
                    source,
                    resource=(
                        file.resource
                        if barrel is not None
                        and barrel.scope == PathSelectionScope.RESOURCE
                        else None
                    ),
                )
                if barrel is not None
                else tuple(
                    output
                    for output in registry.find_emission(source)
                    if ref in output.refs
                )
            )
            if len(candidates) != 1:
                raise PathGraphPlanningError(
                    f"Provider '{source}' resolved {len(candidates)} outputs "
                    f"for '{ref}' required by '{file.node_key}'."
                )
            candidate_path = candidates[0].output_path.as_posix()
            if candidate_path != file.output_path.as_posix():
                dependencies.add(candidate_path)
        result.append(
            replace(file, depends_on=tuple(sorted(dependencies)))
        )
    return result


def _topological_files(files: list[PathGraphFile]) -> list[PathGraphFile]:
    by_path = {file.output_path.as_posix(): file for file in files}
    if len(by_path) != len(files):
        raise PathGraphPlanningError("Planned output paths must be unique.")
    complete: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()
    ordered: list[PathGraphFile] = []

    def visit(path: str) -> None:
        if path in complete:
            return
        if path in active_set:
            start = active.index(path)
            raise PathGraphPlanningError(
                "Planned output cycle: "
                + " -> ".join((*active[start:], path))
            )
        file = by_path[path]
        active.append(path)
        active_set.add(path)
        for dependency in file.depends_on:
            if dependency not in by_path:
                raise PathGraphPlanningError(
                    f"Planned output '{path}' depends on unknown output "
                    f"'{dependency}'."
                )
            visit(dependency)
        active.pop()
        active_set.remove(path)
        complete.add(path)
        ordered.append(file)

    for path in sorted(by_path):
        visit(path)
    return ordered


def _ordered_barrels(
    barrels: tuple[PathBarrel, ...],
) -> tuple[PathBarrel, ...]:
    by_name = {barrel.name: barrel for barrel in barrels}
    complete: set[str] = set()
    ordered: list[PathBarrel] = []

    def visit(barrel: PathBarrel) -> None:
        if barrel.name in complete:
            return
        for exported in barrel.exports:
            nested = by_name.get(exported)
            if nested is not None:
                visit(nested)
        complete.add(barrel.name)
        ordered.append(barrel)

    for barrel in sorted(barrels, key=lambda item: item.name):
        visit(barrel)
    return tuple(ordered)


def _barrel_resources(
    barrel: PathBarrel,
    *,
    exported_nodes: tuple[str, ...],
    registry: VirtualOutputRegistry,
) -> tuple[str | None, ...]:
    if barrel.scope == PathSelectionScope.ALL:
        return (None,)
    return tuple(
        sorted(
            {
                output.resource
                for node in exported_nodes
                for output in registry.find_emission(node)
                if output.resource is not None
            }
        )
    )


def _barrel_members(
    barrel: PathBarrel,
    *,
    exported_nodes: tuple[str, ...],
    registry: VirtualOutputRegistry,
    resource: str | None,
) -> tuple[VirtualOutput, ...]:
    members = tuple(
        output
        for node in exported_nodes
        for output in registry.find_emission(
            node,
            resource=(
                resource
                if barrel.scope == PathSelectionScope.RESOURCE
                else None
            ),
        )
    )
    return tuple(
        sorted(members, key=lambda item: item.output_path.as_posix())
    )


def _expand_output(
    config: PathConfig,
    parts: tuple[Any, ...],
    context: Mapping[str, Any],
) -> Path:
    return expand_template_path(
        Path(*tuple(str(part) for part in parts)),
        context,
        template_extension=config.template_extension,
    )


def _require_template(template_root: Path, relative: str) -> Path:
    path = template_root / Path(relative)
    if not path.is_file():
        raise PathGraphPlanningError(
            f"Configured template does not exist: {relative}"
        )
    return path
