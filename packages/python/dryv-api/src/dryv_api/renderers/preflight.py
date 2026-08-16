from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
from time import sleep

from dryv_api.builds import BuildSession
from dryv_api.contracts import ApiContractError

from .connection import RendererConnection, RendererConnectionState
from .protocol import (
    ContextContractPayload,
    RendererDiagnostic,
    TemplatePayload,
    ValidateTemplateRequest,
)
from .registry import RendererRegistry


@dataclass(frozen=True, slots=True, order=True)
class PreflightKey:
    template_hash: str
    context_contract_hash: str
    renderer_fingerprint: str


@dataclass(frozen=True, slots=True)
class JobPreflight:
    job_id: str
    renderer_fingerprints: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PreflightReport:
    build_id: str
    validated: tuple[PreflightKey, ...]
    jobs: tuple[JobPreflight, ...]

    def permits(self, job_id: str, renderer_fingerprint: str) -> bool:
        job = next((item for item in self.jobs if item.job_id == job_id), None)
        return job is not None and renderer_fingerprint in job.renderer_fingerprints


class TemplatePreflightError(ApiContractError):
    def __init__(
        self,
        job_id: str,
        connection_id: str,
        diagnostics: tuple[RendererDiagnostic, ...],
    ) -> None:
        message = diagnostics[0].message if diagnostics else "renderer rejected template preflight"
        super().__init__(
            "API_TEMPLATE_PREFLIGHT_FAILED",
            f"job {job_id!r} failed on renderer {connection_id!r}: {message}",
        )
        self.job_id = job_id
        self.connection_id = connection_id
        self.diagnostics = diagnostics


class PreflightCoordinator:
    """Validate all currently eligible renderer fingerprints before rendering."""

    def __init__(self, registry: RendererRegistry) -> None:
        self.registry = registry
        self._reports: dict[str, PreflightReport] = {}
        self._lock = Lock()

    def run(self, session: BuildSession) -> PreflightReport:
        with self._lock:
            existing = self._reports.get(session.build_id)
        if existing is not None:
            return existing
        plan = session.plan
        if plan is None:
            raise ApiContractError(
                "API_PLAN_NOT_READY",
                f"build {session.build_id!r} has no GenerationPlan",
            )
        for requirement in plan.required_renderers:
            self.registry.require_capability(requirement.capability)

        validated: dict[PreflightKey, bool] = {}
        jobs: list[JobPreflight] = []
        for job in plan.jobs:
            if session.cancelled:
                raise ApiContractError("API_BUILD_CANCELLED", "build was cancelled during preflight")
            template = session.normalized.resources.require(job.template.resource_id)
            if template.content_hash != job.template.content_hash:
                raise ApiContractError(
                    "API_TEMPLATE_HASH_MISMATCH",
                    f"template resource {job.template.resource_id!r} no longer matches GenerationPlan",
                )
            payload = TemplatePayload(
                template.resource_id,
                template.media_type,
                template.content_hash,
                template.content,
            )
            contract = ContextContractPayload(
                job.context_contract.version,
                job.context_contract.paths,
                job.context_contract.hash,
            )
            by_fingerprint = _fingerprint_groups(
                self.registry.require_capability(job.renderer.capability)
            )
            fingerprints: set[str] = set()
            for fingerprint in sorted(by_fingerprint):
                key = PreflightKey(
                    job.template.content_hash,
                    job.context_contract.hash,
                    fingerprint,
                )
                fingerprints.add(fingerprint)
                if key in validated:
                    continue
                validation_id = _validation_id(key)
                request = ValidateTemplateRequest(
                    validation_id,
                    job.renderer.capability,
                    payload,
                    contract,
                )
                connection = _reserve_preflight(
                    by_fingerprint[fingerprint],
                    session,
                    fingerprint,
                )
                try:
                    result = connection.validate(request)
                finally:
                    connection.release()
                if result.validation_id != validation_id:
                    raise ApiContractError(
                        "API_RENDERER_PROTOCOL",
                        f"renderer {connection.connection_id!r} returned the wrong validation id",
                    )
                if not result.valid:
                    raise TemplatePreflightError(
                        job.id,
                        connection.connection_id,
                        result.diagnostics,
                    )
                validated[key] = True
            if not fingerprints:
                raise ApiContractError(
                    "API_RENDERER_UNAVAILABLE",
                    f"no renderer fingerprints remain for capability {job.renderer.capability!r}",
                )
            jobs.append(JobPreflight(job.id, tuple(sorted(fingerprints))))

        report = PreflightReport(
            session.build_id,
            tuple(sorted(validated)),
            tuple(sorted(jobs, key=lambda item: item.job_id)),
        )
        with self._lock:
            self._reports[session.build_id] = report
        return report

    def report(self, build_id: str) -> PreflightReport | None:
        with self._lock:
            return self._reports.get(build_id)

    def clear(self, build_id: str) -> None:
        with self._lock:
            self._reports.pop(build_id, None)


def _fingerprint_groups(
    connections: tuple[RendererConnection, ...],
) -> dict[str, tuple[RendererConnection, ...]]:
    grouped: dict[str, list[RendererConnection]] = {}
    for connection in connections:
        grouped.setdefault(connection.hello.fingerprint, []).append(connection)
    return {
        fingerprint: tuple(sorted(items, key=lambda item: item.connection_id))
        for fingerprint, items in grouped.items()
    }


def _reserve_preflight(
    connections: tuple[RendererConnection, ...],
    session: BuildSession,
    fingerprint: str,
) -> RendererConnection:
    while True:
        if session.cancelled:
            raise ApiContractError("API_BUILD_CANCELLED", "build was cancelled during preflight")
        ready = tuple(
            connection
            for connection in connections
            if connection.state is RendererConnectionState.READY
        )
        if not ready:
            raise ApiContractError(
                "API_RENDERER_UNAVAILABLE",
                f"renderer fingerprint {fingerprint!r} disconnected during preflight",
            )
        for connection in sorted(
            ready,
            key=lambda item: (item.active / item.hello.max_concurrency, item.connection_id),
        ):
            if connection.reserve():
                return connection
        sleep(0.02)


def _validation_id(key: PreflightKey) -> str:
    payload = "\0".join(
        (key.template_hash, key.context_contract_hash, key.renderer_fingerprint)
    ).encode("utf-8")
    return f"preflight:{sha256(payload).hexdigest()}"


__all__ = [
    "JobPreflight",
    "PreflightCoordinator",
    "PreflightKey",
    "PreflightReport",
    "TemplatePreflightError",
]
