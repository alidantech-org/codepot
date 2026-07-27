from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Callable

from codepotg.plugins import PluginCategory, PluginRegistry
from codepotg.ports import SourceAdapter, TargetAdapter, TemplateEngine


class PluginLoadError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RuntimePlugins:
    source_adapters: tuple[SourceAdapter, ...] = ()
    target_adapters: tuple[TargetAdapter, ...] = ()
    template_engines: tuple[TemplateEngine, ...] = ()

    def __post_init__(self) -> None:
        descriptors = tuple(
            item.plugin
            for item in (
                *self.source_adapters,
                *self.target_adapters,
                *self.template_engines,
            )
        )
        registry = PluginRegistry.build(descriptors)
        if registry.diagnostics.has_errors:
            first = registry.diagnostics.errors[0]
            raise PluginLoadError(f"{first.code}: {first.message}")

    @classmethod
    def discover(cls) -> RuntimePlugins:
        return cls(
            source_adapters=_load_group("codepotg.source_adapters", SourceAdapter),
            target_adapters=_load_group("codepotg.language_adapters", TargetAdapter),
            template_engines=_load_group("codepotg.template_engines", TemplateEngine),
        )

    def source(self, identifier: str) -> SourceAdapter:
        matches = tuple(
            item
            for item in self.source_adapters
            if item.plugin.id == identifier or identifier in item.plugin.aliases
        )
        if len(matches) != 1:
            raise PluginLoadError(f"source adapter {identifier!r} is not available")
        return matches[0]

    def target(self, identifier: str) -> TargetAdapter:
        matches = tuple(
            item
            for item in self.target_adapters
            if any(
                descriptor.id == identifier or identifier in descriptor.aliases
                for descriptor in item.targets
            )
        )
        if len(matches) != 1:
            raise PluginLoadError(f"target adapter {identifier!r} is not available")
        return matches[0]

    def target_for_path(self, path: str) -> tuple[TargetAdapter, str, str]:
        matches: list[tuple[int, str, str, TargetAdapter]] = []
        for adapter in self.target_adapters:
            for descriptor in adapter.targets:
                for suffix in descriptor.extensions:
                    if path.endswith(suffix):
                        matches.append((len(suffix), descriptor.id, suffix, adapter))
        if not matches:
            raise PluginLoadError(f"no target adapter recognizes path {path!r}")
        matches.sort(key=lambda item: (-item[0], item[1], item[2]))
        longest = matches[0][0]
        candidates = tuple(item for item in matches if item[0] == longest)
        if len(candidates) != 1:
            ids = tuple(sorted({item[1] for item in candidates}))
            raise PluginLoadError(
                f"target path {path!r} is ambiguous across {ids!r}"
            )
        _, target_id, suffix, adapter = candidates[0]
        return adapter, target_id, suffix

    def engine(self, identifier: str) -> TemplateEngine:
        matches = tuple(
            item
            for item in self.template_engines
            if item.plugin.id == identifier or identifier in item.plugin.aliases
        )
        if len(matches) != 1:
            raise PluginLoadError(f"template engine {identifier!r} is not available")
        return matches[0]

    def engine_for_path(self, path: str) -> tuple[TemplateEngine, str]:
        matches: list[tuple[int, str, str, TemplateEngine]] = []
        for engine in self.template_engines:
            for suffix in engine.suffixes:
                if path.endswith(suffix):
                    matches.append((len(suffix), engine.plugin.id, suffix, engine))
        if not matches:
            raise PluginLoadError(f"no template engine recognizes path {path!r}")
        matches.sort(key=lambda item: (-item[0], item[1], item[2]))
        longest = matches[0][0]
        candidates = tuple(item for item in matches if item[0] == longest)
        if len(candidates) != 1:
            ids = tuple(sorted({item[1] for item in candidates}))
            raise PluginLoadError(
                f"template path {path!r} is ambiguous across {ids!r}"
            )
        _, _, suffix, engine = candidates[0]
        return engine, suffix


def _load_group(group: str, protocol: type[object]) -> tuple[object, ...]:
    loaded: list[object] = []
    selected = tuple(sorted(entry_points(group=group), key=lambda item: item.name))
    for entry in selected:
        factory = _load_factory(entry)
        try:
            instance = factory()
        except Exception as exc:
            raise PluginLoadError(
                f"plugin factory {group}:{entry.name} failed safely: {type(exc).__name__}"
            ) from exc
        if not isinstance(instance, protocol):
            raise PluginLoadError(
                f"plugin {group}:{entry.name} does not implement the public protocol"
            )
        loaded.append(instance)
    return tuple(loaded)


def _load_factory(entry: EntryPoint) -> Callable[[], object]:
    try:
        factory = entry.load()
    except Exception as exc:
        raise PluginLoadError(
            f"plugin entry point {entry.group}:{entry.name} could not be loaded"
        ) from exc
    if not callable(factory):
        raise PluginLoadError(
            f"plugin entry point {entry.group}:{entry.name} is not a factory"
        )
    return factory
