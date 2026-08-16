from __future__ import annotations

import argparse

from dryv_cli.app.context import AppContext
from dryv_cli.generation import GenerationWorkflow
from dryv_cli.local import LocalEnvironment
from dryv_cli.presentation import render_diagnostics
from dryv_cli.project import discover_project


def validate_command(context: AppContext, args: argparse.Namespace) -> int:
    project = discover_project(context.start)
    build_id: str | None = None
    with LocalEnvironment(context.api_url) as environment:
        workflow = GenerationWorkflow(environment)
        try:
            planned = workflow.plan(project, ir_override=args.ir, author_override=args.author)
            build_id = planned.build_id
            if planned.author_result is not None:
                render_diagnostics(context.console, planned.author_result.diagnostics)
            context.console.write(
                f"Valid: {planned.plan_hash} · {len(planned.artifact_paths)} planned artifact(s)"
            )
            return 0
        finally:
            if build_id is not None:
                workflow.release(build_id)


__all__ = ["validate_command"]
