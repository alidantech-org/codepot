from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from hashlib import sha256
from threading import Event, Lock, Thread

from dryv.features.planning import RenderJob

from dryv_api.builds import BuildSession
from dryv_api.contracts import ApiContractError, BuildDiagnostic
from dryv_api.delivery.streaming import (
    ArtifactData,
    ArtifactFinished,
    ArtifactStarted,
    ArtifactStream,
    ArtifactStreamCancelled,
)

from .connection import RendererConnection
from .preflight import PreflightReport
from .protocol import (
    ArtifactBegin,
    ArtifactChunk,
    ArtifactEnd,
    ContextContractPayload,
    ContextPayload,
    PlannedOutputPayload,
    RenderComplete,
    RenderFailed,
    RenderRequest,
    TemplatePayload,
)
from .registry import RendererRegistry


class RenderExecutionError(ApiContractError):
    pass


@dataclass(frozen=True, slots=True)
class RenderExecution:
    build_id: str
    stream: ArtifactStream
    done: Event
    thread: Thread

    def wait(self, timeout: float | None = None) -> bool:
        return self.done.wait(timeout)


@dataclass(slots=True)
class _ActiveBuild:
    session: BuildSession
    stream: ArtifactStream
    cancelled: Event
    done: Event
    jobs: dict[str, RendererConnection]


class RenderScheduler:
    """Execute ready GenerationPlan jobs over bounded preflight-approved renderer capacity."""

    def __init__(
        self,
        registry: RendererRegistry,
        *,
        max_concurrent_jobs: int = 32,
        max_queued_chunks: int = 32,
        max_chunk_bytes: int = 64 * 1024,
    ) -> None:
        if max_concurrent_jobs < 1:
            raise ValueError("max_concurrent_jobs must be positive")
        self.registry = registry
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_queued_chunks = max_queued_chunks
        self.max_chunk_bytes = max_chunk_bytes
        self._active: dict[str, _ActiveBuild] = {}
        self._lock = Lock()

    def start(self, session: BuildSession, preflight: PreflightReport) -> RenderExecution:
        plan = session.plan
        if plan is None:
            raise ApiContractError("API_PLAN_NOT_READY", "build has no GenerationPlan")
        if preflight.build_id != session.build_id:
            raise ApiContractError("API_PREFLIGHT_BUILD", "preflight report belongs to another build")
        if not session.start_render():
            raise ApiContractError(
                "API_RENDER_STATE",
                f"build {session.build_id!r} is not ready to render",
            )
        stream = ArtifactStream(
            max_chunk_bytes=self.max_chunk_bytes,
            max_queued_chunks=self.max_queued_chunks,
        )
        state = _ActiveBuild(session, stream, Event(), Event(), {})
        with self._lock:
            if session.build_id in self._active:
                raise ApiContractError("API_RENDER_ACTIVE", "build already has active rendering")
            self._active[session.build_id] = state
        thread = Thread(
            target=self._run,
            args=(state, preflight),
            name=f"dryv-render-{session.build_id}",
            daemon=True,
        )
        thread.start()
        return RenderExecution(session.build_id, stream, state.done, thread)

    def cancel(self, build_id: str) -> bool:
        with self._lock:
            state = self._active.get(build_id)
            jobs = () if state is None else tuple(state.jobs.items())
        if state is None:
            return False
        state.cancelled.set()
        state.stream.cancel()
        for job_id, connection in jobs:
            connection.cancel(job_id)
        return True

    def active(self, build_id: str) -> bool:
        with self._lock:
            return build_id in self._active

    def _run(self, state: _ActiveBuild, preflight: PreflightReport) -> None:
        try:
            self._coordinate(state, preflight)
        except ArtifactStreamCancelled:
            if not state.session.cancelled:
                state.session.fail(
                    (
                        BuildDiagnostic(
                            "API_ARTIFACT_STREAM_CANCELLED",
                            "artifact delivery stream was cancelled",
                        ),
                    )
                )
        except ApiContractError as exc:
            if not state.session.cancelled:
                state.session.fail((BuildDiagnostic(exc.code, exc.message),))
        except Exception as exc:
            if not state.session.cancelled:
                state.session.fail((BuildDiagnostic("API_RENDER_FAILED", str(exc)),))
        finally:
            if not state.stream.closed:
                state.stream.close()
            with self._lock:
                self._active.pop(state.session.build_id, None)
            state.done.set()

    def _coordinate(self, state: _ActiveBuild, preflight: PreflightReport) -> None:
        plan = state.session.plan
        assert plan is not None
        pending = {job.id: job for job in plan.jobs}
        completed: set[str] = set()
        running: dict[Future[None], tuple[RenderJob, RendererConnection]] = {}
        executor = ThreadPoolExecutor(
            max_workers=min(self.max_concurrent_jobs, max(1, len(plan.jobs))),
            thread_name_prefix=f"dryv-job-{state.session.build_id}",
        )
        try:
            while pending or running:
                if state.cancelled.is_set() or state.session.cancelled:
                    self._cancel_running(state, running)
                    return

                dispatched = False
                ready = tuple(
                    sorted(
                        (
                            job
                            for job in pending.values()
                            if all(dependency in completed for dependency in job.dependencies)
                        ),
                        key=lambda job: job.order,
                    )
                )
                for job in ready:
                    if len(running) >= self.max_concurrent_jobs:
                        break
                    connection = self._reserve_connection(job, preflight)
                    if connection is None:
                        continue
                    with self._lock:
                        state.jobs[job.id] = connection
                    state.session.render_job_started(job)
                    try:
                        future = executor.submit(self._execute_job, state, job, connection)
                    except Exception:
                        self._release_reservation(state, job.id, connection)
                        raise
                    running[future] = (job, connection)
                    future.add_done_callback(
                        lambda _future, job_id=job.id, reserved=connection: self._release_reservation(
                            state, job_id, reserved
                        )
                    )
                    del pending[job.id]
                    dispatched = True

                if not running:
                    if pending and ready and not dispatched:
                        state.cancelled.wait(0.05)
                        continue
                    if pending and not ready:
                        raise RenderExecutionError(
                            "API_RENDER_DEPENDENCY_DEADLOCK",
                            "no pending render job has satisfied dependencies",
                        )
                    continue

                finished, _ = wait(
                    tuple(running), timeout=0.1, return_when=FIRST_COMPLETED
                )
                for future in finished:
                    job, _connection = running.pop(future)
                    future.result()
                    completed.add(job.id)
                    state.session.render_job_completed(
                        job,
                        completed=len(completed),
                        total=len(plan.jobs),
                    )
            state.session.complete_render()
        finally:
            for future, (job, connection) in tuple(running.items()):
                if not future.done():
                    connection.cancel(job.id)
                    future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)

    def _reserve_connection(
        self,
        job: RenderJob,
        preflight: PreflightReport,
    ) -> RendererConnection | None:
        compatible = tuple(
            connection
            for connection in self.registry.compatible(job.renderer.capability)
            if preflight.permits(job.id, connection.hello.fingerprint)
        )
        if not compatible:
            raise RenderExecutionError(
                "API_RENDERER_PREFLIGHT_MISSING",
                f"no current renderer for job {job.id!r} has an approved preflight fingerprint",
            )
        for connection in sorted(
            compatible,
            key=lambda item: (item.active / item.hello.max_concurrency, item.connection_id),
        ):
            if connection.reserve():
                return connection
        return None

    def _release_reservation(
        self,
        state: _ActiveBuild,
        job_id: str,
        connection: RendererConnection,
    ) -> None:
        with self._lock:
            state.jobs.pop(job_id, None)
        try:
            connection.release()
        except RuntimeError:
            return

    def _execute_job(
        self,
        state: _ActiveBuild,
        job: RenderJob,
        connection: RendererConnection,
    ) -> None:
        stored = state.session.normalized.resources.require(job.template.resource_id)
        request = RenderRequest(
            job.id,
            job.renderer.capability,
            TemplatePayload(
                stored.resource_id,
                stored.media_type,
                stored.content_hash,
                stored.content,
            ),
            ContextPayload(
                1,
                job.context,
                job.context_hash,
                ContextContractPayload(
                    job.context_contract.version,
                    job.context_contract.paths,
                    job.context_contract.hash,
                ),
            ),
            PlannedOutputPayload(job.artifact.id, job.artifact.path),
            {},
        )
        expected_offset = 0
        declared_size: int | None = None
        digest = sha256()
        began = False
        ended = False
        completed = False

        for message in connection.render(request):
            if state.cancelled.is_set() or state.session.cancelled:
                connection.cancel(job.id)
                raise ArtifactStreamCancelled("render build cancelled")
            if completed:
                raise RenderExecutionError(
                    "API_RENDERER_PROTOCOL",
                    f"renderer sent data after completion for job {job.id!r}",
                )
            if isinstance(message, ArtifactBegin):
                if (
                    began
                    or message.job_id != job.id
                    or message.artifact_id != job.artifact.id
                    or message.path != job.artifact.path
                    or not message.media_type
                    or message.media_type.strip() != message.media_type
                    or (message.size is not None and message.size < 0)
                ):
                    raise RenderExecutionError(
                        "API_RENDERER_PROTOCOL",
                        f"invalid artifact begin for job {job.id!r}",
                    )
                began = True
                declared_size = message.size
                state.stream.publish(
                    ArtifactStarted(
                        job.id,
                        job.artifact.id,
                        job.order,
                        job.artifact.path,
                        job.artifact.dependencies,
                        message.media_type,
                        message.size,
                    )
                )
            elif isinstance(message, ArtifactChunk):
                if (
                    not began
                    or ended
                    or message.job_id != job.id
                    or message.artifact_id != job.artifact.id
                    or message.offset != expected_offset
                    or not message.content
                ):
                    raise RenderExecutionError(
                        "API_RENDERER_PROTOCOL",
                        f"invalid artifact chunk for job {job.id!r}",
                    )
                digest.update(message.content)
                offset = message.offset
                for start in range(0, len(message.content), state.stream.max_chunk_bytes):
                    chunk = message.content[start : start + state.stream.max_chunk_bytes]
                    state.stream.publish(
                        ArtifactData(
                            job.id,
                            job.artifact.id,
                            job.order,
                            offset + start,
                            chunk,
                        )
                    )
                expected_offset += len(message.content)
            elif isinstance(message, ArtifactEnd):
                expected_hash = f"sha256:{digest.hexdigest()}"
                if (
                    not began
                    or ended
                    or message.job_id != job.id
                    or message.artifact_id != job.artifact.id
                ):
                    raise RenderExecutionError(
                        "API_RENDERER_PROTOCOL",
                        f"invalid artifact end for job {job.id!r}",
                    )
                if declared_size is not None and message.size != declared_size:
                    raise RenderExecutionError(
                        "API_RENDERER_SIZE_MISMATCH",
                        f"renderer changed declared artifact size for job {job.id!r}",
                    )
                if message.size != expected_offset or message.content_hash != expected_hash:
                    raise RenderExecutionError(
                        "API_RENDERER_HASH_MISMATCH",
                        f"renderer artifact hash/size mismatch for job {job.id!r}",
                    )
                ended = True
                state.stream.publish(
                    ArtifactFinished(
                        job.id,
                        job.artifact.id,
                        job.order,
                        job.artifact.path,
                        message.size,
                        message.content_hash,
                    )
                )
                state.session.artifact_ready(job, message.size, message.content_hash)
            elif isinstance(message, RenderFailed):
                if message.job_id != job.id:
                    raise RenderExecutionError(
                        "API_RENDERER_PROTOCOL",
                        f"renderer failure belongs to another job while rendering {job.id!r}",
                    )
                detail = (
                    message.diagnostics[0].message
                    if message.diagnostics
                    else "renderer reported failure"
                )
                raise RenderExecutionError(
                    "API_RENDERER_FAILED", f"job {job.id!r}: {detail}"
                )
            elif isinstance(message, RenderComplete):
                if message.job_id != job.id or not ended:
                    raise RenderExecutionError(
                        "API_RENDERER_PROTOCOL",
                        f"render completed before artifact end for job {job.id!r}",
                    )
                completed = True
            else:
                raise RenderExecutionError(
                    "API_RENDERER_PROTOCOL",
                    f"unknown renderer message for job {job.id!r}",
                )
        if not began or not ended or not completed:
            raise RenderExecutionError(
                "API_RENDERER_PROTOCOL",
                f"renderer stream ended incompletely for job {job.id!r}",
            )

    def _cancel_running(
        self,
        state: _ActiveBuild,
        running: dict[Future[None], tuple[RenderJob, RendererConnection]],
    ) -> None:
        for future, (job, connection) in tuple(running.items()):
            connection.cancel(job.id)
            future.cancel()
        state.stream.cancel()


__all__ = ["RenderExecution", "RenderExecutionError", "RenderScheduler"]
