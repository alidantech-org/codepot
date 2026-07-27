from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from codepotg.versions import ApiVersion, Version

_PLUGIN_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


class PluginCategory(StrEnum):
    SOURCE_ADAPTER = "source_adapter"
    TARGET_ADAPTER = "target_adapter"
    TEMPLATE_ENGINE = "template_engine"
    PACK_PROVIDER = "pack_provider"
    ECOSYSTEM_ADAPTER = "ecosystem_adapter"
    ARTIFACT_WRITER = "artifact_writer"
    CACHE_STORE = "cache_store"
    COMMAND_EXECUTOR = "command_executor"
    APPROVAL_STORE = "approval_store"
    EVENT_SINK = "event_sink"


class PluginTrust(StrEnum):
    EXECUTABLE = "executable"
    HOST_PROVIDED = "host_provided"


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    id: str
    category: PluginCategory
    distribution: str
    version: Version
    api_version: ApiVersion
    ir_version: ApiVersion | None = None
    aliases: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    trust: PluginTrust = PluginTrust.EXECUTABLE
    documentation: str | None = None

    def __post_init__(self) -> None:
        if _PLUGIN_ID.fullmatch(self.id) is None:
            raise ValueError(f"invalid plugin id: {self.id!r}")
        if not self.distribution:
            raise ValueError("plugin distribution must not be empty")
        _validate_sorted_unique("plugin aliases", self.aliases)
        _validate_sorted_unique("plugin capabilities", self.capabilities)
        if self.id in self.aliases:
            raise ValueError("plugin id must not also be an alias")
        for alias in self.aliases:
            if _PLUGIN_ID.fullmatch(alias) is None:
                raise ValueError(f"invalid plugin alias: {alias!r}")

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


def _validate_sorted_unique(label: str, values: tuple[str, ...]) -> None:
    if tuple(sorted(set(values))) != values:
        raise ValueError(f"{label} must be sorted and unique")
