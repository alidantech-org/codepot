from __future__ import annotations

from dataclasses import dataclass

from dryv.plugins import PluginCategory


@dataclass(frozen=True, slots=True)
class RuntimePluginInfo:
    """Stable, presentation-neutral information about one loaded runtime plugin."""

    id: str
    category: PluginCategory
    distribution: str
    version: str
    aliases: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.distribution or not self.version:
            raise ValueError("runtime plugin information requires id, distribution, and version")
        for label, values in (
            ("aliases", self.aliases),
            ("capabilities", self.capabilities),
            ("provides", self.provides),
        ):
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"runtime plugin {label} must be sorted and unique")


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """Immutable runtime inventory suitable for CLIs, IDEs, HTTP, or MCP adapters."""

    core_version: str
    plugins: tuple[RuntimePluginInfo, ...] = ()

    def __post_init__(self) -> None:
        expected = tuple(sorted(self.plugins, key=lambda item: (item.category.value, item.id)))
        if self.plugins != expected:
            raise ValueError("runtime plugins must be sorted by category and id")
