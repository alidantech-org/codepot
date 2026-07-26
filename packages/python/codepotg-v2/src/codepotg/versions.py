"""Stable public version namespace for CodepotG v2."""

from dataclasses import dataclass

from .core import (
    CORE_VERSION,
    IR_VERSION,
    NAMING_BEHAVIOR_VERSION,
    PLANNING_BEHAVIOR_VERSION,
    PLUGIN_API_VERSION,
    PUBLIC_API_VERSION,
    SELECTION_BEHAVIOR_VERSION,
    ApiVersion,
    BehaviorVersion,
    SemanticVersion,
)

Version = SemanticVersion
IR_API_VERSION = IR_VERSION


@dataclass(frozen=True, slots=True)
class BehaviorVersions:
    naming: BehaviorVersion = NAMING_BEHAVIOR_VERSION
    selection: BehaviorVersion = SELECTION_BEHAVIOR_VERSION
    planning: BehaviorVersion = PLANNING_BEHAVIOR_VERSION


DEFAULT_BEHAVIOR_VERSIONS = BehaviorVersions()

__all__ = [
    "ApiVersion",
    "BehaviorVersion",
    "BehaviorVersions",
    "CORE_VERSION",
    "DEFAULT_BEHAVIOR_VERSIONS",
    "IR_API_VERSION",
    "IR_VERSION",
    "NAMING_BEHAVIOR_VERSION",
    "PLANNING_BEHAVIOR_VERSION",
    "PLUGIN_API_VERSION",
    "PUBLIC_API_VERSION",
    "SELECTION_BEHAVIOR_VERSION",
    "SemanticVersion",
    "Version",
]
