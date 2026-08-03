# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path

import questionary
import typer
from archives.codepotg.cli.presentation.core.console import (
    print_error,
    print_info,
    print_success,
    print_warning,
)

from codepot_file.editor import (
    DEFAULT_INPUT,
    DEFAULT_LANGUAGE,
    DEFAULT_OUTPUT,
    DEFAULT_TASK_NAME,
    TaskDraft,
    init_codepotg_config,
    starter_draft,
)
from codepot_file.loader import CODEPOTG_CONFIG_NAME


def init_command(
    task_name: str | None = typer.Option(None, "--task", help="Initial task name."),
    input_path: str | None = typer.Option(None, "--input", help="OpenAPI input path."),
    language: str | None = typer.Option(None, "--language", help="Generation language."),
    template_dir: str | None = typer.Option(
        None,
        "--template-dir",
        help="Custom template directory. Omit it to use bundled templates.",
    ),
    templates: str | None = typer.Option(
        None,
        "--templates",
        help="Alias for a custom template directory.",
    ),
    output_path: str | None = typer.Option(None, "--output", help="Output directory."),
    clean: list[str] | None = typer.Option(None, "--clean", help="Clean path.", show_default=False),
    before: list[str] | None = typer.Option(
        None,
        "--before",
        help="Before command.",
        show_default=False,
    ),
    after: list[str] | None = typer.Option(
        None,
        "--after",
        help="After command.",
        show_default=False,
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Use starter defaults."),
    force: bool = typer.Option(False, "--force", help=f"Overwrite existing {CODEPOTG_CONFIG_NAME}."),
    debug: bool = typer.Option(False, "--debug", help="Show traceback when an error occurs."),
) -> None:
    """Create ``Codepotg.yaml`` in the current directory."""
    try:
        if force:
            print_warning(f"Overwriting existing {CODEPOTG_CONFIG_NAME} if present.")

        draft = _draft_from_options(
            task_name=task_name,
            input_path=input_path,
            language=language,
            template_dir=template_dir,
            templates=templates,
            output_path=output_path,
            clean=tuple(clean or ()),
            before=tuple(before or ()),
            after=tuple(after or ()),
            yes=yes,
        )
        path = init_codepotg_config(root=Path.cwd(), draft=draft, force=force)
        print_success(f"Created {path.name}")
        print_info(f"Task: {draft.name}")
        if draft.template_dir is None and draft.templates is None:
            print_info(f"Templates: bundled {draft.language or DEFAULT_LANGUAGE} pack")
    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc


def _draft_from_options(
    *,
    task_name: str | None,
    input_path: str | None,
    language: str | None,
    template_dir: str | None,
    templates: str | None,
    output_path: str | None,
    clean: tuple[str, ...],
    before: tuple[str, ...],
    after: tuple[str, ...],
    yes: bool,
) -> TaskDraft:
    if yes:
        starter = starter_draft(task_name or DEFAULT_TASK_NAME)
        return TaskDraft(
            name=starter.name,
            input=input_path or starter.input,
            language=language or starter.language,
            template_dir=template_dir,
            templates=templates,
            output=output_path or starter.output,
            clean=clean,
            before=before,
            after=after,
        )

    if any(
        (
            task_name,
            input_path,
            language,
            template_dir,
            templates,
            output_path,
            clean,
            before,
            after,
        )
    ):
        return TaskDraft(
            name=task_name or DEFAULT_TASK_NAME,
            input=input_path or DEFAULT_INPUT,
            language=language or DEFAULT_LANGUAGE,
            template_dir=template_dir,
            templates=templates,
            output=output_path or DEFAULT_OUTPUT,
            clean=clean,
            before=before,
            after=after,
        )

    return _interactive_draft()


def _interactive_draft() -> TaskDraft:
    task_name = questionary.text("Task name", default=DEFAULT_TASK_NAME).ask() or DEFAULT_TASK_NAME
    input_path = questionary.text("OpenAPI input path", default=DEFAULT_INPUT).ask() or DEFAULT_INPUT
    language = questionary.text("Language", default=DEFAULT_LANGUAGE).ask() or DEFAULT_LANGUAGE
    template_dir = questionary.text(
        "Custom template directory (blank uses bundled templates)",
        default="",
    ).ask()
    output_path = questionary.text("Output directory", default=DEFAULT_OUTPUT).ask() or DEFAULT_OUTPUT
    clean = questionary.text("Clean path (optional)", default="").ask() or ""
    before = questionary.text("Before command (optional)", default="").ask() or ""
    after = questionary.text("After command (optional)", default="").ask() or ""

    return TaskDraft(
        name=task_name,
        input=input_path,
        language=language,
        template_dir=template_dir or None,
        output=output_path,
        clean=(clean,) if clean else (),
        before=(before,) if before else (),
        after=(after,) if after else (),
    )
