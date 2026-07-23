# ruff: noqa: B008

from __future__ import annotations

from pathlib import Path
from typing import Any

import questionary
import typer

from cli.paths import normalize_cli_path
from cli.presentation.core.console import print_error, print_success, print_warning
from codepot_file.editor import (
    DEFAULT_INPUT,
    DEFAULT_LANGUAGE,
    DEFAULT_OUTPUT,
    TaskDraft,
    add_task_to_codepotg_config,
    starter_draft,
)
from codepot_file.loader import CODEPOTG_CONFIG_NAME, load_codepotg_yaml, resolve_codepotg_config

app = typer.Typer(help=f"{CODEPOTG_CONFIG_NAME} task commands.", no_args_is_help=True)


@app.command("add")
def add_task_command(
    task_name: str = typer.Argument(..., help="Task name to add."),
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
    yes: bool = typer.Option(False, "--yes", "-y", help="Use flags/defaults without prompting."),
    force: bool = typer.Option(False, "--force", help="Replace existing task."),
    debug: bool = typer.Option(False, "--debug", help="Show traceback when an error occurs."),
) -> None:
    """Add a task to ``Codepotg.yaml``."""
    try:
        resolved_config = normalize_cli_path(config_path)
        if force:
            print_warning(f"Replacing task '{task_name}' if it exists.")

        draft = _draft_from_options(
            task_name=task_name,
            config_path=resolved_config,
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
        path = add_task_to_codepotg_config(
            config_path=resolved_config,
            draft=draft,
            force=force,
            yes=yes,
        )
        print_success(f"Added task '{task_name}' to {path.name}")
    except Exception as exc:
        print_error(str(exc))
        if debug:
            raise
        raise typer.Exit(1) from exc


def _draft_from_options(
    *,
    task_name: str,
    config_path: Path | None,
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
        return TaskDraft(
            name=task_name,
            input=input_path,
            language=language,
            template_dir=template_dir,
            templates=templates,
            output=output_path,
            clean=clean,
            before=before,
            after=after,
        )

    if any((input_path, language, template_dir, templates, output_path, clean, before, after)):
        starter = starter_draft(task_name)
        return TaskDraft(
            name=task_name,
            input=input_path or starter.input,
            language=language or starter.language,
            template_dir=template_dir,
            templates=templates,
            output=output_path or starter.output,
            clean=clean,
            before=before,
            after=after,
        )

    return _interactive_draft(task_name, config_path=config_path)


def _interactive_draft(task_name: str, *, config_path: Path | None) -> TaskDraft:
    defaults = _load_defaults(config_path)

    input_path = _ask_with_default("OpenAPI input path", DEFAULT_INPUT, defaults.get("input"))
    language = _ask_with_default("Language", DEFAULT_LANGUAGE, defaults.get("language"))
    template_default = defaults.get("templateDir") or defaults.get("templates")
    template_dir = _ask_optional(
        "Custom template directory (blank uses bundled templates)",
        template_default,
    )
    output_path = _ask_with_default("Output directory", DEFAULT_OUTPUT, defaults.get("output"))
    clean = questionary.text("Clean path (optional)", default="").ask() or ""
    before = _ask_with_default(
        "Before command (optional)",
        "",
        _first_command(defaults.get("before")),
    )
    after = _ask_with_default("After command (optional)", "", _first_command(defaults.get("after")))

    return TaskDraft(
        name=task_name,
        input=input_path,
        language=language,
        template_dir=template_dir,
        output=output_path,
        clean=(clean,) if clean else (),
        before=(before,) if before else (),
        after=(after,) if after else (),
    )


def _load_defaults(config_path: Path | None) -> dict[str, Any]:
    path = resolve_codepotg_config(config_path)
    raw = load_codepotg_yaml(path)
    defaults = raw.get("defaults")
    return defaults if isinstance(defaults, dict) else {}


def _ask_with_default(label: str, fallback: str, inherited: Any) -> str | None:
    if isinstance(inherited, str) and inherited.strip():
        answer = questionary.text(
            f"{label} (blank uses defaults: {inherited})",
            default="",
        ).ask()
        return answer or None
    return questionary.text(label, default=fallback).ask() or fallback


def _ask_optional(label: str, inherited: Any) -> str | None:
    default = inherited if isinstance(inherited, str) else ""
    answer = questionary.text(label, default=default).ask()
    return answer.strip() if isinstance(answer, str) and answer.strip() else None


def _first_command(raw: Any) -> str | None:
    if isinstance(raw, list) and raw:
        item = raw[0]
        if isinstance(item, str):
            return item
        if isinstance(item, dict) and isinstance(item.get("run"), str):
            return item["run"]
    return None
