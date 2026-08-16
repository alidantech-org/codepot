from __future__ import annotations

from pathlib import Path

from dryv_cli.commands import compile_command, generate_command, plan_command, validate_command
from dryv_cli.presentation import Console, render_exception

from .arguments import build_parser
from .context import AppContext


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    context = AppContext(Path(args.project).resolve(), args.api, Console())
    try:
        if args.command == "validate":
            return validate_command(context, args)
        if args.command == "compile":
            return compile_command(context, args)
        if args.command == "plan":
            return plan_command(context, args)
        if args.command == "generate":
            return generate_command(context, args)
        parser.error(f"unknown command {args.command!r}")
    except KeyboardInterrupt:
        context.console.error("Cancelled")
        return 130
    except Exception as exc:
        render_exception(context.console, exc)
        return 1
    return 1


__all__ = ["run"]
