# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path

import typer

from cli.paths import normalize_cli_path
from cli.presentation.core.console import (
    print_error,
    print_header,
    print_info,
    print_success,
)
from cli.presentation.core.reporter import Reporter


def paths_command(
    ctx: typer.Context,
    template_root: Path = typer.Argument(
        ...,
        help="Template pack directory containing paths.yaml or paths.yml.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    debug: bool = typer.Option(False, "--debug", help="Show traceback on failure."),
) -> None:
    """Validate and inspect a template pack paths configuration."""
    try:
        from cli.main import get_runtime

        resolved = normalize_cli_path(template_root)
        if resolved is None:
            raise ValueError("Template root is required.")

        reporter = Reporter(verbose=True)
        print_header("Paths", str(resolved))
        result = get_runtime(ctx).paths(resolved, progress=reporter.event)

        print_success(
            f"Resolved: {result.config_path or '(default path configuration)'}"
        )
        print_info(f"Imports: {result.import_strategy}")
        print_info(
            "Templates: "
            f"extension={result.template_extension}, "
            f"strip={str(result.strip_template_extension).lower()}, "
            f"raw={str(result.allow_raw_files).lower()}"
        )
        print_info(f"Default lifecycle: {result.default_lifecycle}")

        if not result.folders:
            print_info("Folder recipes: none")
            return

        reporter.section("Folder Recipes")
        for folder in result.folders:
            select = folder.select or "(root context)"
            lifecycle = folder.lifecycle or result.default_lifecycle
            parts = "/".join(folder.parts)
            print_info(
                f"{folder.name}: select={select}; as={folder.alias}; "
                f"mode={folder.mode}; lifecycle={lifecycle}; parts={parts}"
            )
    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
