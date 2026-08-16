from __future__ import annotations

from threading import Lock

from dryv.runtime import DryvRuntime

from .builds import BuildManager, BuildSession
from .contracts import ApiContractError, BuildDiagnostic, CreateBuildRequest, DeliveryMode
from .delivery import BundleBuilder, BundleHandle
from .renderers import (
    PreflightCoordinator,
    PreflightReport,
    RenderExecution,
    RenderScheduler,
    RendererConnection,
    RendererRegistry,
    TemplatePreflightError,
)


class DryvApiServer:
    """Application service for Runtime planning, render coordination and delivery."""

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
        self.scheduler = RenderScheduler(self.renderers)
        self.bundles = BundleBuilder()
        self._executions: dict[str, RenderExecution] = {}
        self._stream_consumers: set[str] = set()
        self._lock = Lock()

    def accept_build(self, request: CreateBuildRequest) -> BuildSession:
        return self.builds.create(request)

    def plan_build(self, build_id: str) -> BuildSession:
        return self.builds.run(build_id)

    def submit_build(self, request: CreateBuildRequest) -> BuildSession:
        return self.plan_build(self.accept_build(request).build_id)

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
                        for key, value in (("line", item.line), ("column", item.column))
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

    def render_build(self, build_id: str) -> RenderExecution:
        session = self.builds.require(build_id)
        report = self.preflight.report(build_id)
        if report is None:
            raise ApiContractError(
                "API_PREFLIGHT_REQUIRED",
                f"build {build_id!r} must complete renderer preflight before rendering",
            )
        execution = self.scheduler.start(session, report)
        with self._lock:
            if build_id in self._executions:
                self.scheduler.cancel(build_id)
                raise ApiContractError("API_RENDER_ACTIVE", "build already has retained execution")
            self._executions[build_id] = execution
        if session.normalized.delivery is DeliveryMode.BUNDLE:
            self.bundles.start(session, execution.stream)
        return execution

    def register_renderer(self, connection: RendererConnection) -> None:
        self.renderers.register(connection)

    def unregister_renderer(self, connection_id: str, *, close: bool = True) -> bool:
        return self.renderers.unregister(connection_id, close=close)

    def build(self, build_id: str) -> BuildSession:
        return self.builds.require(build_id)

    def execution(self, build_id: str) -> RenderExecution | None:
        with self._lock:
            return self._executions.get(build_id)

    def bundle(self, build_id: str) -> BundleHandle | None:
        return self.bundles.get(build_id)

    def claim_stream_consumer(self, build_id: str) -> bool:
        session = self.builds.require(build_id)
        if session.normalized.delivery is not DeliveryMode.STREAM:
            raise ApiContractError(
                "API_STREAM_DELIVERY",
                f"build {build_id!r} is not configured for stream delivery",
            )
        with self._lock:
            if build_id in self._stream_consumers:
                return False
            self._stream_consumers.add(build_id)
            return True

    def release_stream_consumer(self, build_id: str) -> None:
        with self._lock:
            self._stream_consumers.discard(build_id)

    def cancel_build(self, build_id: str) -> bool:
        changed = self.builds.cancel(build_id)
        self.scheduler.cancel(build_id)
        return changed

    def release_build(self, build_id: str) -> bool:
        execution = self.execution(build_id)
        if execution is not None and not execution.done.is_set():
            raise ApiContractError(
                "API_RENDER_ACTIVE",
                f"build {build_id!r} cannot be released while renderer work is still active",
            )
        bundle = self.bundle(build_id)
        if bundle is not None and not bundle.ready.is_set():
            raise ApiContractError(
                "API_BUNDLE_ACTIVE",
                f"build {build_id!r} cannot be released while bundle packaging is still active",
            )
        released = self.builds.release(build_id)
        if not released:
            return False
        self.preflight.clear(build_id)
        self.bundles.release(build_id)
        with self._lock:
            self._executions.pop(build_id, None)
            self._stream_consumers.discard(build_id)
        return True


__all__ = ["DryvApiServer"]
