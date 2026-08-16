from __future__ import annotations

import argparse

from dryv_api import BuildStatus, DeliveryMode

from dryv_cli.app.context import AppContext
from dryv_cli.artifacts import ArtifactSet, receive_bundle, receive_stream
from dryv_cli.filesystem import apply_changes, build_change_set, load_managed_state
from dryv_cli.generation import GenerationWorkflow, publish_events
from dryv_cli.local import LocalEnvironment
from dryv_cli.presentation import ProgressPrinter, render_apply_result, render_changes
from dryv_cli.project import discover_project


def generate_command(context: AppContext, args: argparse.Namespace) -> int:
    project = discover_project(context.start)
    delivery = DeliveryMode(args.delivery)
    build_id: str | None = None
    with LocalEnvironment(context.api_url) as environment:
        workflow = GenerationWorkflow(environment)
        try:
            planned = workflow.plan(
                project,
                delivery=delivery,
                ir_override=args.ir,
                author_override=args.author,
            )
            build_id = planned.build_id
            workflow.render(planned)
            progress = ProgressPrinter(context.console)
            artifacts = _receive(environment, planned, progress, delivery)
            with artifacts:
                managed = load_managed_state(project.root)
                changes = build_change_set(project.root, artifacts, managed, force=args.force)
                render_changes(context.console, changes)
                if changes.conflicts:
                    context.console.error("Conflicts must be resolved or explicitly overwritten with --force.")
                    return 2
                if args.dry_run:
                    context.console.write("Dry run: no generated files were written.")
                    return 0
                result = apply_changes(project.root, changes, managed)
                render_apply_result(context.console, result)
                return 0
        except BaseException:
            if build_id is not None:
                try:
                    workflow.cancel(build_id)
                except Exception:
                    pass
            raise
        finally:
            if build_id is not None:
                try:
                    workflow.release(build_id)
                except Exception:
                    pass


def _receive(
    environment: LocalEnvironment,
    planned: object,
    progress: ProgressPrinter,
    delivery: DeliveryMode,
) -> ArtifactSet:
    if delivery is DeliveryMode.STREAM:
        return receive_stream(environment.api, planned, progress=progress)  # type: ignore[arg-type]
    for _ in publish_events(environment.api.events(planned.build_id), progress):  # type: ignore[attr-defined]
        pass
    summary = environment.api.get_build(planned.build_id)  # type: ignore[attr-defined]
    if summary.status is not BuildStatus.RENDER_COMPLETE:
        message = summary.diagnostics[0].message if summary.diagnostics else f"build ended as {summary.status.value}"
        raise RuntimeError(message)
    return receive_bundle(environment.api, planned)  # type: ignore[arg-type]


__all__ = ["generate_command"]
