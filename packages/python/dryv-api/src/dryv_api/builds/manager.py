from __future__ import annotations

from threading import Lock

from dryv.runtime import DryvRuntime

from dryv_api.contracts import ApiContractError, BuildDiagnostic, BuildStatus, CreateBuildRequest
from dryv_api.resources.bundle import normalize_build

from .session import BuildSession


class BuildManager:
    """Own active build sessions and invoke the public Dryv Runtime boundary."""

    def __init__(self, runtime: DryvRuntime | None = None) -> None:
        self.runtime = runtime or DryvRuntime()
        self._sessions: dict[str, BuildSession] = {}
        self._lock = Lock()

    def create(self, request: CreateBuildRequest) -> BuildSession:
        with self._lock:
            if request.build_id in self._sessions:
                raise ApiContractError(
                    "API_BUILD_EXISTS",
                    f"build {request.build_id!r} already exists",
                )
        normalized = normalize_build(request)
        session = BuildSession(normalized)
        with self._lock:
            if request.build_id in self._sessions:
                raise ApiContractError(
                    "API_BUILD_EXISTS",
                    f"build {request.build_id!r} already exists",
                )
            self._sessions[request.build_id] = session
        session.accepted()
        return session

    def run(self, build_id: str) -> BuildSession:
        session = self.require(build_id)
        if not session.start_planning():
            return session
        result = self.runtime.plan(
            session.normalized.runtime_input,
            events=session.runtime_event,
        )
        if session.cancelled:
            return session
        if result.success and result.plan is not None:
            session.complete_plan(result.plan)
            return session
        diagnostics = tuple(
            BuildDiagnostic(
                item.code,
                item.message,
                item.level,
                item.subject,
                item.details,
            )
            for item in result.diagnostics
        )
        if not diagnostics:
            diagnostics = (
                BuildDiagnostic(
                    "API_RUNTIME_FAILED",
                    "Dryv Runtime failed without a diagnostic",
                ),
            )
        session.fail(diagnostics)
        return session

    def get(self, build_id: str) -> BuildSession | None:
        with self._lock:
            return self._sessions.get(build_id)

    def require(self, build_id: str) -> BuildSession:
        session = self.get(build_id)
        if session is None:
            raise ApiContractError("API_BUILD_MISSING", f"build {build_id!r} does not exist")
        return session

    def cancel(self, build_id: str) -> bool:
        return self.require(build_id).cancel()

    def release(self, build_id: str) -> bool:
        with self._lock:
            session = self._sessions.get(build_id)
            if session is None:
                return False
            if session.status not in {
                BuildStatus.PLAN_READY,
                BuildStatus.CANCELLED,
                BuildStatus.FAILED,
            }:
                raise ApiContractError(
                    "API_BUILD_ACTIVE",
                    f"build {build_id!r} cannot be released while active",
                )
            del self._sessions[build_id]
            return True

    def active_ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._sessions))


__all__ = ["BuildManager"]
