from __future__ import annotations

import queue
import threading
import time
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class SchedulingError(ValueError):
    def __init__(self, code: str, message: str, *, job_id: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.job_id = job_id


class RetrySafeTransportError(RuntimeError):
    """A transport failure that may be retried without duplicating semantic work."""


class WorkerDisconnectedError(RetrySafeTransportError):
    pass


class JobStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class QueueLimits:
    context: int = 32
    render: int = 32
    results: int = 32
    artifacts: int = 16
    events: int = 64

    def __post_init__(self) -> None:
        for name in ("context", "render", "results", "artifacts", "events"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} queue limit must be positive")


class BoundedChannel(Generic[T]):
    """Blocking bounded channel used to make backpressure an explicit contract."""

    def __init__(self, maxsize: int) -> None:
        if maxsize < 1:
            raise ValueError("bounded channel maxsize must be positive")
        self._queue: queue.Queue[T] = queue.Queue(maxsize=maxsize)
        self._max_observed = 0
        self._lock = threading.Lock()

    @property
    def maxsize(self) -> int:
        return self._queue.maxsize

    @property
    def max_observed(self) -> int:
        with self._lock:
            return self._max_observed

    @property
    def size(self) -> int:
        return self._queue.qsize()

    def put(self, value: T, *, timeout: float | None = None) -> None:
        self._queue.put(value, block=True, timeout=timeout)
        with self._lock:
            self._max_observed = max(self._max_observed, self._queue.qsize())

    def get(self, *, timeout: float | None = None) -> T:
        return self._queue.get(block=True, timeout=timeout)

    def task_done(self) -> None:
        self._queue.task_done()

    def join(self) -> None:
        self._queue.join()


@dataclass(frozen=True, slots=True)
class ScheduleChannels:
    context: BoundedChannel[object]
    render: BoundedChannel[object]
    results: BoundedChannel[object]
    artifacts: BoundedChannel[object]
    events: BoundedChannel[object]

    @classmethod
    def create(cls, limits: QueueLimits = QueueLimits()) -> ScheduleChannels:
        return cls(
            context=BoundedChannel(limits.context),
            render=BoundedChannel(limits.render),
            results=BoundedChannel(limits.results),
            artifacts=BoundedChannel(limits.artifacts),
            events=BoundedChannel(limits.events),
        )


@dataclass(frozen=True, slots=True)
class ScheduledJob:
    id: str
    required_capability: str
    dependencies: tuple[str, ...] = ()
    order: int = 0
    timeout_seconds: float | None = None
    max_attempts: int = 1
    payload: object = None

    def __post_init__(self) -> None:
        if not self.id or self.id.strip() != self.id:
            raise ValueError("scheduled job id must be a non-empty trimmed string")
        if not self.required_capability or self.required_capability.strip() != self.required_capability:
            raise ValueError("scheduled jobs require a capability")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("scheduled job dependencies must be unique")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("scheduled job timeout must be positive")
        if self.max_attempts < 1:
            raise ValueError("scheduled job max_attempts must be positive")


@dataclass(frozen=True, slots=True)
class WorkerCapacity:
    worker_id: str
    capabilities: tuple[str, ...]
    max_concurrency: int = 1

    def __post_init__(self) -> None:
        if not self.worker_id or self.worker_id.strip() != self.worker_id:
            raise ValueError("worker id must be a non-empty trimmed string")
        if self.max_concurrency < 1:
            raise ValueError("worker max_concurrency must be positive")
        if not self.capabilities or len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("worker capabilities must be non-empty and unique")


class WorkSession(Protocol):
    def capacity(self) -> WorkerCapacity: ...

    def execute(self, job: ScheduledJob) -> object: ...

    def cancel(self, job_id: str) -> None: ...


class CancellationToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()


@dataclass(frozen=True, slots=True)
class JobResult:
    job_id: str
    status: JobStatus
    worker_id: str | None
    attempts: int
    value: object = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SchedulingMetrics:
    max_in_flight: int
    dispatches: int
    retries: int
    worker_dispatches: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class ScheduleReport:
    results: tuple[JobResult, ...]
    metrics: SchedulingMetrics

    @property
    def success(self) -> bool:
        return all(item.status is JobStatus.SUCCEEDED for item in self.results)

    def result(self, job_id: str) -> JobResult | None:
        return next((item for item in self.results if item.job_id == job_id), None)


@dataclass(slots=True)
class _InFlight:
    job: ScheduledJob
    session: WorkSession
    worker_id: str
    attempt: int
    started_at: float


class SchedulingFeature:
    """Bounded, dependency-aware work dispatcher.

    Planning supplies dependency-ready job facts. Runtime supplies compatible established
    sessions. This Feature owns only dispatch/capacity/backpressure/cancellation behavior.
    """

    def __init__(self, *, poll_interval_seconds: float = 0.01) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError("scheduler poll interval must be positive")
        self._poll_interval = poll_interval_seconds

    def create_channels(self, limits: QueueLimits = QueueLimits()) -> ScheduleChannels:
        return ScheduleChannels.create(limits)

    def run(
        self,
        jobs: Sequence[ScheduledJob],
        sessions: Sequence[WorkSession],
        *,
        cancellation: CancellationToken | None = None,
        on_dispatch: Callable[[ScheduledJob, WorkerCapacity, int], None] | None = None,
    ) -> ScheduleReport:
        cancellation = cancellation or CancellationToken()
        ordered_jobs = _validate_jobs(jobs)
        workers = _validate_sessions(sessions)
        capacities = {worker.worker_id: worker for worker in workers}
        sessions_by_id = {session.capacity().worker_id: session for session in sessions}
        total_capacity = sum(worker.max_concurrency for worker in workers)
        if ordered_jobs and total_capacity < 1:
            raise SchedulingError("SCHEDULE_NO_WORKERS", "no worker sessions are available")

        slots = {worker.worker_id: worker.max_concurrency for worker in workers}
        cursor: dict[str, int] = defaultdict(int)
        attempts: dict[str, int] = defaultdict(int)
        worker_dispatches: dict[str, int] = defaultdict(int)
        completed: dict[str, JobResult] = {}
        in_flight: dict[Future[object], _InFlight] = {}
        dispatches = 0
        retries = 0
        max_in_flight = 0

        executor = ThreadPoolExecutor(max_workers=max(1, total_capacity), thread_name_prefix="dryv-scheduler")
        try:
            while len(completed) < len(ordered_jobs):
                if cancellation.cancelled:
                    for state in tuple(in_flight.values()):
                        state.session.cancel(state.job.id)
                    for job in ordered_jobs:
                        if job.id not in completed:
                            completed[job.id] = JobResult(
                                job.id, JobStatus.CANCELLED, None, attempts[job.id], error="build cancelled"
                            )
                    break

                progress = False
                for job in ordered_jobs:
                    if job.id in completed or any(state.job.id == job.id for state in in_flight.values()):
                        continue
                    dependency_results = [completed.get(dep) for dep in job.dependencies]
                    if any(result is not None and result.status is not JobStatus.SUCCEEDED for result in dependency_results):
                        completed[job.id] = JobResult(
                            job.id,
                            JobStatus.BLOCKED,
                            None,
                            attempts[job.id],
                            error="required dependency did not succeed",
                        )
                        progress = True
                        continue
                    if not all(result is not None for result in dependency_results):
                        continue

                    session = _choose_session(
                        job.required_capability,
                        workers,
                        sessions_by_id,
                        slots,
                        cursor,
                    )
                    if session is None:
                        continue
                    worker = capacities[session.capacity().worker_id]
                    attempts[job.id] += 1
                    attempt = attempts[job.id]
                    slots[worker.worker_id] -= 1
                    future = executor.submit(session.execute, job)
                    in_flight[future] = _InFlight(job, session, worker.worker_id, attempt, time.monotonic())
                    dispatches += 1
                    worker_dispatches[worker.worker_id] += 1
                    max_in_flight = max(max_in_flight, len(in_flight))
                    if on_dispatch is not None:
                        on_dispatch(job, worker, attempt)
                    progress = True

                if len(completed) >= len(ordered_jobs):
                    break

                if not in_flight:
                    unresolved = [job for job in ordered_jobs if job.id not in completed]
                    missing_capability = next(
                        (
                            job
                            for job in unresolved
                            if not any(job.required_capability in worker.capabilities for worker in workers)
                        ),
                        None,
                    )
                    if missing_capability is not None:
                        raise SchedulingError(
                            "SCHEDULE_NO_CAPABILITY",
                            f"no worker provides capability {missing_capability.required_capability!r}",
                            job_id=missing_capability.id,
                        )
                    if not progress:
                        raise SchedulingError(
                            "SCHEDULE_STALLED",
                            "scheduler cannot make progress with the supplied dependency/capacity graph",
                        )
                    continue

                done, _ = wait(
                    tuple(in_flight),
                    timeout=self._poll_interval,
                    return_when=FIRST_COMPLETED,
                )

                now = time.monotonic()
                timed_out = [
                    future
                    for future, state in in_flight.items()
                    if state.job.timeout_seconds is not None
                    and now - state.started_at >= state.job.timeout_seconds
                ]
                for future in timed_out:
                    state = in_flight.pop(future)
                    slots[state.worker_id] += 1
                    state.session.cancel(state.job.id)
                    completed[state.job.id] = JobResult(
                        state.job.id,
                        JobStatus.TIMED_OUT,
                        state.worker_id,
                        state.attempt,
                        error="job timed out",
                    )
                    future.cancel()

                for future in done:
                    state = in_flight.pop(future, None)
                    if state is None:
                        continue
                    slots[state.worker_id] += 1
                    try:
                        value = future.result()
                    except RetrySafeTransportError as exc:
                        if state.attempt < state.job.max_attempts and not cancellation.cancelled:
                            retries += 1
                            progress = True
                            continue
                        completed[state.job.id] = JobResult(
                            state.job.id,
                            JobStatus.FAILED,
                            state.worker_id,
                            state.attempt,
                            error=str(exc) or type(exc).__name__,
                        )
                    except Exception as exc:  # noqa: BLE001 - session failures become structured results
                        completed[state.job.id] = JobResult(
                            state.job.id,
                            JobStatus.FAILED,
                            state.worker_id,
                            state.attempt,
                            error=str(exc) or type(exc).__name__,
                        )
                    else:
                        completed[state.job.id] = JobResult(
                            state.job.id,
                            JobStatus.SUCCEEDED,
                            state.worker_id,
                            state.attempt,
                            value=value,
                        )
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        result_order = {job.id: (job.order, job.id) for job in ordered_jobs}
        results = tuple(sorted(completed.values(), key=lambda item: result_order[item.job_id]))
        metrics = SchedulingMetrics(
            max_in_flight=max_in_flight,
            dispatches=dispatches,
            retries=retries,
            worker_dispatches=tuple(sorted(worker_dispatches.items())),
        )
        return ScheduleReport(results, metrics)


def _validate_jobs(jobs: Sequence[ScheduledJob]) -> tuple[ScheduledJob, ...]:
    ordered = tuple(sorted(jobs, key=lambda item: (item.order, item.id)))
    identities = tuple(job.id for job in ordered)
    if len(identities) != len(set(identities)):
        raise SchedulingError("SCHEDULE_DUPLICATE_JOB", "scheduled job ids must be unique")
    known = set(identities)
    for job in ordered:
        missing = tuple(dep for dep in job.dependencies if dep not in known)
        if missing:
            raise SchedulingError(
                "SCHEDULE_MISSING_DEPENDENCY",
                f"job {job.id!r} depends on missing job {missing[0]!r}",
                job_id=job.id,
            )
    _assert_acyclic(ordered)
    return ordered


def _assert_acyclic(jobs: Iterable[ScheduledJob]) -> None:
    graph = {job.id: job.dependencies for job in jobs}
    active: list[str] = []
    done: set[str] = set()

    def visit(identity: str) -> None:
        if identity in done:
            return
        if identity in active:
            cycle = " -> ".join((*active[active.index(identity) :], identity))
            raise SchedulingError("SCHEDULE_DEPENDENCY_CYCLE", f"job dependency cycle: {cycle}", job_id=identity)
        active.append(identity)
        try:
            for dependency in graph[identity]:
                visit(dependency)
        finally:
            active.pop()
        done.add(identity)

    for identity in sorted(graph):
        visit(identity)


def _validate_sessions(sessions: Sequence[WorkSession]) -> tuple[WorkerCapacity, ...]:
    workers = tuple(sorted((session.capacity() for session in sessions), key=lambda item: item.worker_id))
    identities = tuple(worker.worker_id for worker in workers)
    if len(identities) != len(set(identities)):
        raise SchedulingError("SCHEDULE_DUPLICATE_WORKER", "worker ids must be unique")
    return workers


def _choose_session(
    capability: str,
    workers: Sequence[WorkerCapacity],
    sessions_by_id: Mapping[str, WorkSession],
    slots: Mapping[str, int],
    cursor: dict[str, int],
) -> WorkSession | None:
    compatible = [
        worker
        for worker in workers
        if capability in worker.capabilities and slots[worker.worker_id] > 0
    ]
    if not compatible:
        return None
    index = cursor[capability] % len(compatible)
    cursor[capability] += 1
    return sessions_by_id[compatible[index].worker_id]


__all__ = [
    "BoundedChannel",
    "CancellationToken",
    "JobResult",
    "JobStatus",
    "QueueLimits",
    "RetrySafeTransportError",
    "ScheduleChannels",
    "ScheduleReport",
    "ScheduledJob",
    "SchedulingError",
    "SchedulingFeature",
    "SchedulingMetrics",
    "WorkerCapacity",
    "WorkerDisconnectedError",
    "WorkSession",
]
