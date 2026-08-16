from __future__ import annotations

from threading import Lock

from dryv.features.planning import GenerationPlan
from dryv.runtime import RuntimeEvent

from dryv_api.contracts import BuildDiagnostic, BuildStatus, BuildSummary
from dryv_api.resources.bundle import NormalizedBuild

from .events import BuildEvent, BuildEventType, runtime_build_event

_TERMINAL = {BuildStatus.PLAN_READY, BuildStatus.CANCELLED, BuildStatus.FAILED}


class BuildSession:
    """Isolated in-memory state for one stateless V1 build."""

    def __init__(self, normalized: NormalizedBuild) -> None:
        self.normalized = normalized
        self.build_id = normalized.runtime_input.build_id
        self._status = BuildStatus.ACCEPTED
        self._plan: GenerationPlan | None = None
        self._diagnostics: tuple[BuildDiagnostic, ...] = ()
        self._events: list[BuildEvent] = []
        self._sequence = 0
        self._lock = Lock()

    @property
    def status(self) -> BuildStatus:
        with self._lock:
            return self._status

    @property
    def plan(self) -> GenerationPlan | None:
        with self._lock:
            return self._plan

    @property
    def cancelled(self) -> bool:
        return self.status is BuildStatus.CANCELLED

    def accepted(self) -> None:
        self.emit(BuildEventType.ACCEPTED, "Build request accepted")
        self.emit(BuildEventType.RESOURCES_READY, "Build resources normalized and verified")

    def start_planning(self) -> bool:
        with self._lock:
            if self._status in _TERMINAL:
                return False
            self._status = BuildStatus.PLANNING
        return True

    def runtime_event(self, event: RuntimeEvent) -> None:
        with self._lock:
            if self._status is BuildStatus.CANCELLED:
                return
            sequence = self._next_sequence_locked()
            self._events.append(runtime_build_event(sequence, event))

    def complete_plan(self, plan: GenerationPlan) -> bool:
        with self._lock:
            if self._status is BuildStatus.CANCELLED:
                return False
            self._plan = plan
            self._status = BuildStatus.PLAN_READY
            sequence = self._next_sequence_locked()
            self._events.append(
                BuildEvent(
                    sequence,
                    self.build_id,
                    BuildEventType.PLAN_READY,
                    "GenerationPlan is ready for renderer prerequisites",
                    details=(
                        ("planHash", plan.plan_hash),
                        ("jobs", str(len(plan.jobs))),
                        ("artifacts", str(len(plan.artifacts))),
                    ),
                )
            )
            return True

    def fail(self, diagnostics: tuple[BuildDiagnostic, ...]) -> bool:
        with self._lock:
            if self._status is BuildStatus.CANCELLED:
                return False
            self._diagnostics = diagnostics
            self._status = BuildStatus.FAILED
            for diagnostic in diagnostics:
                sequence = self._next_sequence_locked()
                self._events.append(
                    BuildEvent(
                        sequence,
                        self.build_id,
                        BuildEventType.DIAGNOSTIC,
                        diagnostic.message,
                        diagnostic.subject,
                        diagnostic.details,
                    )
                )
            sequence = self._next_sequence_locked()
            self._events.append(
                BuildEvent(sequence, self.build_id, BuildEventType.FAILED, "Build planning failed")
            )
            return True

    def cancel(self) -> bool:
        with self._lock:
            if self._status in _TERMINAL:
                return False
            self._status = BuildStatus.CANCELLED
            sequence = self._next_sequence_locked()
            self._events.append(
                BuildEvent(sequence, self.build_id, BuildEventType.CANCELLED, "Build cancelled")
            )
            return True

    def emit(
        self,
        event_type: BuildEventType,
        message: str,
        *,
        subject: str | None = None,
        details: tuple[tuple[str, str], ...] = (),
    ) -> None:
        with self._lock:
            sequence = self._next_sequence_locked()
            self._events.append(
                BuildEvent(sequence, self.build_id, event_type, message, subject, details)
            )

    def events(self, *, after_sequence: int = 0) -> tuple[BuildEvent, ...]:
        with self._lock:
            return tuple(item for item in self._events if item.sequence > after_sequence)

    def summary(self) -> BuildSummary:
        with self._lock:
            plan = self._plan
            return BuildSummary(
                self.build_id,
                self._status,
                None if plan is None else plan.plan_hash,
                0 if plan is None else len(plan.jobs),
                0 if plan is None else len(plan.artifacts),
                self._diagnostics,
            )

    def _next_sequence_locked(self) -> int:
        self._sequence += 1
        return self._sequence


__all__ = ["BuildSession"]
