from __future__ import annotations

from codepotg.plugins import PluginCategory, PluginDescriptor, PluginRegistry
from codepotg.versions import PLUGIN_API_VERSION, Version


def test_plugin_registry_detects_identifier_conflicts() -> None:
    first = PluginDescriptor(
        id="first",
        aliases=("shared",),
        category=PluginCategory.TARGET_ADAPTER,
        distribution="first-package",
        version=Version.parse("1.0.0"),
        api_version=PLUGIN_API_VERSION,
    )
    second = PluginDescriptor(
        id="second",
        aliases=("shared",),
        category=PluginCategory.TARGET_ADAPTER,
        distribution="second-package",
        version=Version.parse("1.0.0"),
        api_version=PLUGIN_API_VERSION,
    )

    registry = PluginRegistry.build((second, first))

    assert registry.diagnostics.has_errors
    assert registry.resolve(PluginCategory.TARGET_ADAPTER, "shared") is None
    assert registry.resolve(PluginCategory.TARGET_ADAPTER, "first") == first
