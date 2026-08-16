from __future__ import annotations

import argparse

from dryv_cli.app.context import AppContext
from dryv_cli.generation import GenerationWorkflow
from dryv_cli.local import LocalEnvironment
from dryv_cli.presentation import render_plan
from dryv_cli.project import discover_project


def plan_command(context: AppContext, args: argparse.Namespace) -> int:
    project = discover_project(context.start)
    build_id: str | None = None
    with LocalEnvironment(context.api_url) as environment:
        workflow = GenerationWorkflow(environment)
        try:
            planned = workflow.plan(project, ir_override=args.ir, author_override=args.author)
            build_id = planned.build_id
            render_plan(context.console, planned.plan, full_json=args.json)
            return 0
        finally:
            if build_id is not None:
                workflow.release(build_id)


__all__ = ["plan_command"]
