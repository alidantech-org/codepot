from __future__ import annotations

from dryv.features.artifacts import ArtifactFeature
from dryv.features.authoring import AuthoringFeature
from dryv.features.cache import CacheFeature
from dryv.features.ir import IRFeature
from dryv.features.planning import PlanningFeature
from dryv.features.scheduling import SchedulingFeature
from dryv.features.templating import TemplatingFeature

from .engine import DryvRuntime


def create_runtime(
    *,
    cache: CacheFeature | None = None,
    ir: IRFeature | None = None,
    planning: PlanningFeature | None = None,
    authoring: AuthoringFeature | None = None,
    templating: TemplatingFeature | None = None,
    scheduling: SchedulingFeature | None = None,
    artifacts: ArtifactFeature | None = None,
) -> DryvRuntime:
    """Create one transport-neutral Dryv Engine composition root."""

    return DryvRuntime(
        cache=cache,
        ir=ir,
        planning=planning,
        authoring=authoring,
        templating=templating,
        scheduling=scheduling,
        artifacts=artifacts,
    )


__all__ = ["DryvRuntime", "create_runtime"]
