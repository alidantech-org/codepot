# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path

import typer
from archives.codepotg.cli.paths import normalize_cli_path
from archives.codepotg.cli.presentation.core.console import (
    console,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)
from archives.codepotg.cli.presentation.core.reporter import Reporter
from archives.codepotg.cli.presentation.emit.files import render_emit_files

from codepot_file.loader import CODEPOTG_CONFIG_NAME


def generate_command(
    ctx: typer.Context,
    task_name: str | None = typer.Argument(None, help="Task name from Codepotg.yaml."),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to Codepotg.yaml or another explicit CodepotG YAML config.",
        exists=False,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    all_tasks: bool = typer.Option(False, "--all", help="Run all tasks in file order."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print planned actions without writing."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show command output and files."),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Clean configured paths first."),
    skip_before: bool = typer.Option(False, "--skip-before", help="Skip before commands."),
    skip_after: bool = typer.Option(False, "--skip-after", help="Skip after commands."),
    debug: bool = typer.Option(False, "--debug", help="Show traceback when an error occurs."),
) -> None:
    """Run generation from ``Codepotg.yaml``."""
    try:
        from archives.codepotg.cli.main import get_runtime

        resolved_config = normalize_cli_path(config_path)
        reporter = Reporter(verbose=verbose)

        runtime = get_runtime(ctx)
        print_header("Generate", str(resolved_config or CODEPOTG_CONFIG_NAME))
        result = runtime.generate(
            config_path=resolved_config,
            task_name=task_name,
            all_tasks=all_tasks,
            dry_run=dry_run,
            verbose=verbose,
            refresh=refresh,
            skip_before=skip_before,
            skip_after=skip_after,
            progress=reporter.event,
        )

        reporter.step("Summary")

        for task in result.tasks:
            print_success(f"{task.name}: {task.language} -> {task.output_path}")
            print_info(f"Input: {task.input_path}")
            print_info(f"Templates: {task.template_dir}")

            if task.cleaned:
                for path in task.cleaned:
                    print_info(f"{'Would clean' if dry_run else 'Cleaned'}: {path}")

            managed_written = max(len(task.written) - len(task.immutable_created), 0)
            print_info(
                "Managed: "
                f"{managed_written} created, {len(task.updated)} updated, "
                f"{len(task.unchanged)} unchanged"
            )
            print_info(
                "Immutable: "
                f"{len(task.immutable_created)} created, "
                f"{len(task.immutable_skipped)} skipped existing"
            )
            if task.refused:
                print_warning(f"Refused: {len(task.refused)} unsafe write(s)")

            if verbose:
                render_emit_files("Planned Files", task.planned)
                if not dry_run:
                    render_emit_files("Written Files", task.written)
                    render_emit_files("Updated Files", task.updated)
                    render_emit_files("Unchanged Files", task.unchanged)
                    render_emit_files("Skipped Files", task.skipped)

            for diagnostic in task.diagnostics:
                if diagnostic.level == "warning":
                    print_warning(diagnostic.message)
                elif verbose:
                    print_info(diagnostic.message)

        console.print()
        print_success(f"Completed {len(result.tasks)} task(s).")

    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc
