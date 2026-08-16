from __future__ import annotations

from dryv.features.ir import IRFeature
from dryv.features.planning import PlanningFeature
from dryv.versions import CORE_VERSION

from .contracts import RuntimeSnapshot

_FEATURES = (
    "serialization",
    "project",
    "resources",
    "hashing",
    "ir",
    "packs",
    "planning",
    "cache",
    "diagnostics",
)


class DryvRuntime:
    """Small composition root for deterministic Dryv planning."""

    def __init__(
        self,
        *,
        ir: IRFeature | None = None,
        planning: PlanningFeature | None = None,
    ) -> None:
        self.ir = ir or IRFeature()
        self.planning = planning or PlanningFeature()

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(core_version=str(CORE_VERSION), features=_FEATURES)


__all__ = ["DryvRuntime"]
