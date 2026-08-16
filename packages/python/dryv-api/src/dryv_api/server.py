from __future__ import annotations

from dryv.runtime import DryvRuntime

from .builds import BuildManager, BuildSession
from .contracts import CreateBuildRequest


class DryvApiServer:
    """Small API composition root around one reusable Dryv Runtime."""

    def __init__(
        self,
        *,
        runtime: DryvRuntime | None = None,
        builds: BuildManager | None = None,
    ) -> None:
        if runtime is not None and builds is not None:
            raise ValueError("provide either runtime or BuildManager, not both")
        self.builds = builds or BuildManager(runtime)

    def accept_build(self, request: CreateBuildRequest) -> BuildSession:
        return self.builds.create(request)

    def plan_build(self, build_id: str) -> BuildSession:
        return self.builds.run(build_id)

    def submit_build(self, request: CreateBuildRequest) -> BuildSession:
        session = self.accept_build(request)
        return self.plan_build(session.build_id)

    def build(self, build_id: str) -> BuildSession:
        return self.builds.require(build_id)

    def cancel_build(self, build_id: str) -> bool:
        return self.builds.cancel(build_id)

    def release_build(self, build_id: str) -> bool:
        return self.builds.release(build_id)


__all__ = ["DryvApiServer"]
