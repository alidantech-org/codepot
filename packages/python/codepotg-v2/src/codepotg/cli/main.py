from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from codepotg.application import generate
from codepotg.runtime.composition import generate_to_files


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)

    if arguments.command == "plan":
        result = generate(arguments.project, dry_run=True)
        _print_result(result)
        return 0 if result.ok else 1

    if arguments.command == "generate":
        if arguments.memory:
            result = generate(arguments.project)
            _print_result(result)
            return 0 if result.ok else 1
        result, report = generate_to_files(
            arguments.project,
            destination=arguments.destination,
        )
        _print_result(result, report=report)
        return 0 if result.ok else 1

    parser.error("a command is required")
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codepotg",
        description="Plan and generate CodepotG v2 projects.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="Validate and print the complete artifact plan.")
    plan.add_argument("project", nargs="?", default="codepotg.yaml")

    generate_command = commands.add_parser(
        "generate",
        help="Render and transactionally write generated artifacts.",
    )
    generate_command.add_argument("project", nargs="?", default="codepotg.yaml")
    generate_command.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="Destination root. Defaults to the project configuration directory.",
    )
    generate_command.add_argument(
        "--memory",
        action="store_true",
        help="Render in memory without writing files.",
    )
    return parser


def _print_result(result: object, *, report: object | None = None) -> None:
    status = getattr(result, "status", "failed")
    diagnostics = getattr(result, "diagnostics", ())
    data = getattr(result, "data", None)
    plan = getattr(data, "plan", None)
    output = getattr(data, "output", None)

    payload: dict[str, object] = {
        "status": str(status),
        "diagnostics": (diagnostics.to_dict() if hasattr(diagnostics, "to_dict") else ()),
        "artifacts": tuple(
            {
                "id": item.id,
                "kind": item.kind.value,
                "path": item.output_path,
                "selection": item.selection_key,
                "semanticId": item.semantic_id,
                "target": item.target_id,
                "template": item.template_id,
            }
            for item in (getattr(plan, "artifacts", ()) or ())
        ),
    }
    if output is not None:
        payload["generated"] = tuple(
            {
                "bytes": len(item.content),
                "path": item.path,
                "semanticId": item.semantic_id,
                "target": item.target_id,
            }
            for item in output.artifacts
        )
    if report is not None:
        payload["writes"] = tuple(
            {"kind": item.kind.value, "path": item.path} for item in report.changes
        )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
