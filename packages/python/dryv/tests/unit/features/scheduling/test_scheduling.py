from __future__ import annotations

import threading
import time

from dryv.features.scheduling import (
    BoundedChannel,
    CancellationToken,
    JobStatus,
    RetrySafeTransportError,
    ScheduledJob,
    SchedulingFeature,
    WorkerCapacity,
)


class FakeSession:
    def __init__(
        self,
        worker_id: str,
        *,
        capability: str = "render/jinja",
        max_concurrency: int = 1,
        delay: float = 0.0,
        fail_once: bool = False,
    ) -> None:
        self._capacity = WorkerCapacity(worker_id, (capability,), max_concurrency)
        self.delay = delay
        self.fail_once = fail_once
        self.calls: list[str] = []
        self.cancelled: list[str] = []
        self._failed: set[str] = set()

    def capacity(self) -> WorkerCapacity:
        return self._capacity

    def execute(self, job: ScheduledJob) -> object:
        self.calls.append(job.id)
        if self.delay:
            time.sleep(self.delay)
        if self.fail_once and job.id not in self._failed:
            self._failed.add(job.id)
            raise RetrySafeTransportError("temporary disconnect")
        return f"{self._capacity.worker_id}:{job.id}"

    def cancel(self, job_id: str) -> None:
        self.cancelled.append(job_id)


def test_bounded_channel_applies_backpressure() -> None:
    channel: BoundedChannel[str] = BoundedChannel(1)
    channel.put("first")
    released = threading.Event()

    def producer() -> None:
        channel.put("second")
        released.set()

    thread = threading.Thread(target=producer)
    thread.start()
    time.sleep(0.02)
    assert not released.is_set()
    assert channel.get() == "first"
    thread.join(timeout=1)
    assert released.is_set()
    assert channel.max_observed == 1


def test_independent_jobs_use_available_capacity_and_results_stay_deterministic() -> None:
    sessions = (
        FakeSession("worker-a", max_concurrency=1, delay=0.03),
        FakeSession("worker-b", max_concurrency=1, delay=0.005),
    )
    jobs = (
        ScheduledJob("b", "render/jinja", order=2),
        ScheduledJob("a", "render/jinja", order=1),
    )
    report = SchedulingFeature(poll_interval_seconds=0.001).run(jobs, sessions)
    assert report.success
    assert [item.job_id for item in report.results] == ["a", "b"]
    assert report.metrics.max_in_flight == 2
    assert dict(report.metrics.worker_dispatches) == {"worker-a": 1, "worker-b": 1}


def test_dependencies_wait_for_required_upstream_result() -> None:
    session = FakeSession("worker")
    jobs = (
        ScheduledJob("parent", "render/jinja", order=1),
        ScheduledJob("child", "render/jinja", dependencies=("parent",), order=2),
    )
    report = SchedulingFeature().run(jobs, (session,))
    assert report.success
    assert session.calls == ["parent", "child"]


def test_retry_safe_transport_failure_retries_without_poisoning_result() -> None:
    session = FakeSession("worker", fail_once=True)
    report = SchedulingFeature().run(
        (ScheduledJob("job", "render/jinja", max_attempts=2),),
        (session,),
    )
    assert report.success
    assert report.results[0].attempts == 2
    assert report.metrics.retries == 1


def test_non_retryable_failure_blocks_dependents() -> None:
    class Failing(FakeSession):
        def execute(self, job: ScheduledJob) -> object:
            if job.id == "parent":
                raise ValueError("bad template")
            return super().execute(job)

    report = SchedulingFeature().run(
        (
            ScheduledJob("parent", "render/jinja", order=1),
            ScheduledJob("child", "render/jinja", dependencies=("parent",), order=2),
        ),
        (Failing("worker"),),
    )
    assert not report.success
    assert report.result("parent").status is JobStatus.FAILED  # type: ignore[union-attr]
    assert report.result("child").status is JobStatus.BLOCKED  # type: ignore[union-attr]


def test_build_cancellation_propagates_to_in_flight_session() -> None:
    token = CancellationToken()
    session = FakeSession("worker", delay=0.05)

    def cancel_soon() -> None:
        time.sleep(0.01)
        token.cancel()

    thread = threading.Thread(target=cancel_soon)
    thread.start()
    report = SchedulingFeature(poll_interval_seconds=0.001).run(
        (ScheduledJob("job", "render/jinja"),),
        (session,),
        cancellation=token,
    )
    thread.join(timeout=1)
    assert not report.success
    assert report.results[0].status is JobStatus.CANCELLED
    assert session.cancelled == ["job"]


def test_timeout_is_terminal_and_calls_session_cancel() -> None:
    session = FakeSession("worker", delay=0.05)
    report = SchedulingFeature(poll_interval_seconds=0.001).run(
        (ScheduledJob("job", "render/jinja", timeout_seconds=0.005),),
        (session,),
    )
    assert report.results[0].status is JobStatus.TIMED_OUT
    assert session.cancelled == ["job"]
