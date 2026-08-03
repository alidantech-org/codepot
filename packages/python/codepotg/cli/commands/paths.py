# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path

import typer

from archives.codepotg.cli.paths import normalize_cli_path
from archives.codepotg.cli.presentation.core.console import (
    print_error,
    print_header,
    print_info,
    print_success,
)
from archives.codepotg.cli.presentation.core.reporter import Reporter


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
    """Validate and review a template pack paths configuration."""

    try:
        from archives.codepotg.cli.main import get_runtime

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

        if result.folders:
            reporter.section("Legacy Folder Recipes")
            for folder in result.folders:
                select = folder.select or "(root context)"
                lifecycle = folder.lifecycle or result.default_lifecycle
                parts = "/".join(folder.parts)
                print_info(
                    f"{folder.name}: select={select}; as={folder.alias}; "
                    f"mode={folder.mode}; lifecycle={lifecycle}; parts={parts}"
                )
        else:
            print_info("Legacy folder recipes: none")

        if result.selections:
            reporter.section("Selections")
            for selection in result.selections:
                print_info(
                    f"{selection.name}: select={selection.select}; "
                    f"as={selection.alias}; scope={selection.scope}"
                )
        else:
            print_info("Selections: none")

        if result.emissions:
            reporter.section("Emissions")
            for emission in result.emissions:
                lifecycle = emission.lifecycle or result.default_lifecycle
                output = "/".join(emission.output)
                providers = ", ".join(
                    f"{provider.purpose}={provider.source}"
                    for provider in emission.providers
                ) or "none"
                provides = ", ".join(emission.provides) or "none"
                print_info(
                    f"{emission.name}: selection={emission.selection}; "
                    f"template={emission.template}; output={output}; "
                    f"lifecycle={lifecycle}; provides={provides}; providers={providers}"
                )
        else:
            print_info("Emissions: none")

        if result.barrels:
            reporter.section("Barrels")
            for barrel in result.barrels:
                lifecycle = barrel.lifecycle or result.default_lifecycle
                output = "/".join(barrel.output)
                exports = ", ".join(barrel.exports)
                print_info(
                    f"{barrel.name}: template={barrel.template}; output={output}; "
                    f"scope={barrel.scope}; as={barrel.alias}; lifecycle={lifecycle}; "
                    f"exports={exports}"
                )
        else:
            print_info("Barrels: none")
    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
