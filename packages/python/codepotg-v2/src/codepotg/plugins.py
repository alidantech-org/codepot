from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .core import (
    ApiVersion,
    Diagnostic,
    DiagnosticSeverity,
    Diagnostics,
    SemanticVersion,
)

_PLUGIN_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


class PluginCategory(str, Enum):
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


class PluginTrust(str, Enum):
    EXECUTABLE = "executable"
    HOST_PROVIDED = "host_provided"


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    id: str
    category: PluginCategory
    distribution: str
    version: SemanticVersion
    api_version: ApiVersion
    ir_version: SemanticVersion | None = None
    aliases: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    trust: PluginTrust = PluginTrust.EXECUTABLE
    documentation: str | None = None

    def __post_init__(self) -> None:
        if not _PLUGIN_ID.fullmatch(self.id):
            raise ValueError(f"invalid plugin id: {self.id!r}")
        if not self.distribution:
            raise ValueError("plugin distribution must not be empty")
        _validate_sorted_unique("plugin aliases", self.aliases)
        _validate_sorted_unique("plugin capabilities", self.capabilities)
        if self.id in self.aliases:
            raise ValueError("plugin id must not also be an alias")
        for alias in self.aliases:
            if not _PLUGIN_ID.fullmatch(alias):
                raise ValueError(f"invalid plugin alias: {alias!r}")

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True, slots=True)
class PluginRegistry:
    descriptors: tuple[PluginDescriptor, ...]
    diagnostics: Diagnostics = Diagnostics()

    @classmethod
    def build(cls, descriptors: tuple[PluginDescriptor, ...]) -> PluginRegistry:
        ordered = tuple(sorted(descriptors, key=lambda item: (item.category.value, item.id)))
        diagnostics: list[Diagnostic] = []
        owners: dict[tuple[PluginCategory, str], PluginDescriptor] = {}

        for descriptor in ordered:
            for identifier in (descriptor.id, *descriptor.aliases):
                key = (descriptor.category, identifier)
                previous = owners.get(key)
                if previous is None:
                    owners[key] = descriptor
                    continue
                diagnostics.append(
                    Diagnostic(
                        code="PLUGIN_IDENTIFIER_CONFLICT",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"plugin identifier {identifier!r} is claimed by both "
                            f"{previous.id!r} and {descriptor.id!r}"
                        ),
                        details=(
                            ("category", descriptor.category.value),
                            ("identifier", identifier),
                        ),
                    )
                )

        return cls(ordered, Diagnostics(tuple(diagnostics)).sorted())

    def resolve(self, category: PluginCategory, identifier: str) -> PluginDescriptor | None:
        matches = tuple(
            descriptor
            for descriptor in self.descriptors
            if descriptor.category is category
            and (descriptor.id == identifier or identifier in descriptor.aliases)
        )
        return matches[0] if len(matches) == 1 else None

    def require_capabilities(
        self,
        category: PluginCategory,
        identifier: str,
        capabilities: tuple[str, ...],
    ) -> Diagnostics:
        descriptor = self.resolve(category, identifier)
        if descriptor is None:
            return Diagnostics(
                (
                    Diagnostic(
                        code="PLUGIN_NOT_FOUND",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"plugin {category.value}:{identifier} is not available",
                        details=(("category", category.value), ("identifier", identifier)),
                    ),
                )
            )
        missing = tuple(sorted(set(capabilities) - set(descriptor.capabilities)))
        if not missing:
            return Diagnostics()
        return Diagnostics(
            (
                Diagnostic(
                    code="PLUGIN_CAPABILITY_MISSING",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"plugin {descriptor.id!r} is missing required capabilities",
                    details=(
                        ("capabilities", missing),
                        ("plugin", descriptor.id),
                    ),
                ),
            )
        )


def _validate_sorted_unique(label: str, values: tuple[str, ...]) -> None:
    if tuple(sorted(set(values))) != values:
        raise ValueError(f"{label} must be sorted and unique")
