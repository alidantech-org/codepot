from __future__ import annotations

from typing import TYPE_CHECKING

from codepotg.plugins import PluginCategory, PluginDescriptor, PluginTrust
from codepotg.versions import IR_API_VERSION, PLUGIN_API_VERSION, Version

from .version import DESCRIPTOR_VERSION

if TYPE_CHECKING:
    from .adapter import OpenApiSourceAdapter

PLUGIN = PluginDescriptor(
    id="openapi",
    category=PluginCategory.SOURCE_ADAPTER,
    distribution="codepotg-openapi",
    version=Version.parse(DESCRIPTOR_VERSION),
    api_version=PLUGIN_API_VERSION,
    ir_version=IR_API_VERSION,
    capabilities=(
        "input.local",
        "input.memory",
        "openapi.3.0",
        "openapi.3.1",
        "references.local",
    ),
    trust=PluginTrust.EXECUTABLE,
    documentation="OpenAPI 3.0/3.1 source adapter for the closed CodepotG v2 kernel.",
)


def create_plugin() -> OpenApiSourceAdapter:
    from .adapter import OpenApiSourceAdapter

    return OpenApiSourceAdapter()
