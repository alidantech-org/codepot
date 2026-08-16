from __future__ import annotations

from dryv.runtime import DryvRuntime

from .builds import BuildManager, BuildSession
from .contracts import ApiContractError, BuildDiagnostic, CreateBuildRequest
from .renderers import (
    PreflightCoordinator,
    PreflightReport,
    RendererConnection,
    RendererRegistry,
    TemplatePreflightError,
)


class DryvApiServer:
    """Small API composition root around Runtime, builds and Render Client inventory."""

    def __init__(
        self,
        *,
        runtime: DryvRuntime | None = None,
        builds: BuildManager | None = None,
        renderers: RendererRegistry | None = None,
    ) -> None:
        if runtime is not None and builds is not None:
            raise ValueError("provide either runtime or BuildManager, not both")
        self.builds = builds or BuildManager(runtime)
        self.renderers = renderers or RendererRegistry()
        self.preflight = PreflightCoordinator(self.renderers)

    def accept_build(self, request: CreateBuildRequest) -> BuildSession:
        return self.builds.create(request)

    def plan_build(self, build_id: str) -> BuildSession:
        return self.builds.run(build_id)

    def submit_build(self, request: CreateBuildRequest) -> BuildSession:
        session = self.accept_build(request)
        return self.plan_build(session.build_id)

    def preflight_build(self, build_id: str) -> PreflightReport | None:
        session = self.builds.require(build_id)
        if not session.start_preflight():
            return self.preflight.report(build_id)
        try:
            report = self.preflight.run(session)
        except TemplatePreflightError as exc:
            diagnostics = tuple(
                BuildDiagnostic(
                    item.code,
                    item.message,
                    "error",
                    item.path,
                    tuple(
                        (key, str(value))
                        for key, value in (
                            ("line", item.line),
                            ("column", item.column),
                        )
                        if value is not None
                    ),
                )
                for item in exc.diagnostics
            )
            session.fail(
                diagnostics
                or (BuildDiagnostic(exc.code, exc.message, "error", exc.job_id),)
            )
            return None
        except ApiContractError as exc:
            session.fail((BuildDiagnostic(exc.code, exc.message),))
            return None
        except Exception as exc:
            session.fail((BuildDiagnostic("API_PREFLIGHT_FAILED", str(exc)),))
            return None
        session.complete_preflight(validations=len(report.validated))
        return report

    def prepare_build(self, request: CreateBuildRequest) -> BuildSession:
        session = self.submit_build(request)
        if session.plan is not None:
            self.preflight_build(session.build_id)
        return session

    def register_renderer(self, connection: RendererConnection) -> None:
        self.renderers.register(connection)

    def unregister_renderer(self, connection_id: str) -> bool:
        return self.renderers.unregister(connection_id)

    def build(self, build_id: str) -> BuildSession:
        return self.builds.require(build_id)

    def cancel_build(self, build_id: str) -> bool:
        return self.builds.cancel(build_id)

    def release_build(self, build_id: str) -> bool:
        released = self.builds.release(build_id)
        if released:
            self.preflight.clear(build_id)
        return released


__all__ = ["DryvApiServer"]
