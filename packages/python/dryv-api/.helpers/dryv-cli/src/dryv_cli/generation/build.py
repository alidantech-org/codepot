from __future__ import annotations

from dataclasses import dataclass

from dryv_api import BuildStatus, DeliveryMode

from dryv_cli.connections.author import AuthorClient
from dryv_cli.local import LocalEnvironment
from dryv_cli.project import LocalProject

from .plan import artifact_paths, plan_hash, required_renderers
from .request import CollectedBuild, collect_build_request


class GenerationWorkflowError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class PlannedBuild:
    build_id: str
    plan: dict[str, object]
    delivery: DeliveryMode
    author_result: object | None = None

    @property
    def required_renderers(self) -> tuple[str, ...]:
        return required_renderers(self.plan)

    @property
    def artifact_paths(self) -> tuple[str, ...]:
        return artifact_paths(self.plan)

    @property
    def plan_hash(self) -> str:
        return plan_hash(self.plan)


@dataclass(frozen=True, slots=True)
class RunningBuild:
    planned: PlannedBuild

    @property
    def build_id(self) -> str:
        return self.planned.build_id


class GenerationWorkflow:
    def __init__(
        self,
        environment: LocalEnvironment,
        *,
        author: AuthorClient | None = None,
    ) -> None:
        self.environment = environment
        self.author = author or AuthorClient()

    def plan(
        self,
        project: LocalProject,
        *,
        delivery: DeliveryMode = DeliveryMode.STREAM,
        ir_override: str | None = None,
        author_override: str | None = None,
    ) -> PlannedBuild:
        collected: CollectedBuild = collect_build_request(
            project,
            author=self.author,
            delivery=delivery,
            ir_override=ir_override,
            author_override=author_override,
        )
        summary = self.environment.api.create_build(collected.request)
        if summary.status is BuildStatus.FAILED:
            message = summary.diagnostics[0].message if summary.diagnostics else "Dryv Runtime planning failed"
            raise GenerationWorkflowError("CLI_PLAN_FAILED", message)
        if summary.status is not BuildStatus.PLAN_READY:
            raise GenerationWorkflowError(
                "CLI_PLAN_STATE",
                f"dryv-api returned unexpected planning state {summary.status.value!r}",
            )
        plan = self.environment.api.get_plan(collected.request.build_id)
        return PlannedBuild(
            collected.request.build_id,
            plan,
            delivery,
            collected.author_result,
        )

    def render(self, planned: PlannedBuild) -> RunningBuild:
        self.environment.ensure_renderers(planned.required_renderers)
        preflight = self.environment.api.preflight(planned.build_id)
        if preflight.status is BuildStatus.FAILED:
            message = preflight.diagnostics[0].message if preflight.diagnostics else "template preflight failed"
            raise GenerationWorkflowError("CLI_PREFLIGHT_FAILED", message)
        if preflight.status is not BuildStatus.RENDER_READY:
            raise GenerationWorkflowError(
                "CLI_PREFLIGHT_STATE",
                f"dryv-api returned unexpected preflight state {preflight.status.value!r}",
            )
        rendering = self.environment.api.render(planned.build_id)
        if rendering.status not in {BuildStatus.RENDERING, BuildStatus.RENDER_COMPLETE}:
            raise GenerationWorkflowError(
                "CLI_RENDER_STATE",
                f"dryv-api returned unexpected render state {rendering.status.value!r}",
            )
        return RunningBuild(planned)

    def cancel(self, build_id: str) -> None:
        self.environment.api.cancel(build_id)

    def release(self, build_id: str) -> None:
        self.environment.api.release(build_id)


__all__ = [
    "GenerationWorkflow",
    "GenerationWorkflowError",
    "PlannedBuild",
    "RunningBuild",
]
