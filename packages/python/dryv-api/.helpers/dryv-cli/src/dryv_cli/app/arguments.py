from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dryv", description="Deterministic software generation through Dryv")
    parser.add_argument("--project", default=".", help="project path used to discover dryv.yaml")
    parser.add_argument("--api", help="use an already-running dryv-api instead of the temporary local host")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate Author/IR, project configuration and packs")
    _source_overrides(validate)

    compile_parser = commands.add_parser("compile", help="compile Author source into Canonical Dryv IR")
    compile_parser.add_argument("--author", help="Author target override (module[:attribute] or Python file target)")
    compile_parser.add_argument("--format", choices=("json", "jsonl", "yaml"), default="json")
    compile_parser.add_argument("-o", "--output", help="write Canonical IR under the project root instead of stdout")

    plan = commands.add_parser("plan", help="produce and inspect the deterministic GenerationPlan")
    _source_overrides(plan)
    plan.add_argument("--json", action="store_true", help="print the complete canonical plan document")

    generate = commands.add_parser("generate", help="render, verify, diff and apply generated artifacts")
    _source_overrides(generate)
    generate.add_argument("--delivery", choices=("stream", "bundle"), default="stream")
    generate.add_argument("--dry-run", action="store_true", help="show changes without writing generated files")
    generate.add_argument("--force", action="store_true", help="explicitly overwrite conflicting regular files")
    return parser


def _source_overrides(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--ir", help="Canonical IR file override")
    source.add_argument("--author", help="Author target override")


__all__ = ["build_parser"]
