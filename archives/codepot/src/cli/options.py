"""Shared CLI option and value resolution helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from archives.codepot.src.cli.constants import options as opt
from archives.codepot.src.cli.constants.defaults import (
    DEFAULT_LANGUAGE,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SPEC_PATH,
    DEFAULT_TEMPLATE_PACKAGE_PATH,
)
from archives.codepot.src.cli.presentation.prompts import (
    ask_dry_run,
    ask_force,
    ask_format,
    ask_inspect_mode,
    ask_language,
    ask_only_groups,
    ask_output_path,
    ask_run_hooks,
    ask_select,
    ask_show_context,
    ask_show_dependencies,
    ask_show_imports,
    ask_show_paths,
    ask_skip_static,
    ask_spec_path,
    ask_strict,
    ask_template_ids,
    ask_template_package_path,
    ask_templates_path,
)


def spec_argument():
    return typer.Argument(help=opt.HELP_SPEC)


def language_option():
    return typer.Option("--language", "-l", help=opt.HELP_LANGUAGE)


def templates_option():
    return typer.Option("--template-package", "-t", help=opt.HELP_TEMPLATE_PACKAGE)


def output_option():
    return typer.Option("--out", "-o", help=opt.HELP_OUT)


def only_option():
    return typer.Option("--only", help=opt.HELP_ONLY)


def select_option():
    return typer.Option("--select", help=opt.HELP_SELECT)


def template_option():
    return typer.Option("--template", help=opt.HELP_TEMPLATE)


def json_option():
    return typer.Option("--json", help=opt.HELP_JSON)


def quiet_option():
    return typer.Option("--quiet", "-q", help=opt.HELP_QUIET)


def verbose_option():
    return typer.Option("--verbose", "-v", help=opt.HELP_VERBOSE)


def debug_option():
    return typer.Option("--debug", help=opt.HELP_DEBUG)


def interactive_option():
    return typer.Option("--interactive", "-I", help=opt.HELP_INTERACTIVE)


def parse_csv(value: str | None) -> tuple[str, ...]:
    """Parse comma-separated values."""

    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def parse_only(value: str | None) -> tuple[str, ...]:
    """Parse comma-separated template IDs."""

    return parse_csv(value)


def resolve_spec_path(value: Path | None, *, interactive: bool) -> Path:
    """Resolve spec path from CLI or prompt/default."""

    if interactive:
        return ask_spec_path(value or DEFAULT_SPEC_PATH)

    return value or DEFAULT_SPEC_PATH


def resolve_language(value: str | None, *, interactive: bool) -> str:
    """Resolve target language."""

    if interactive:
        return ask_language(value or DEFAULT_LANGUAGE)

    return value or DEFAULT_LANGUAGE


def resolve_output_path(value: Path | None, *, interactive: bool) -> Path:
    """Resolve output path."""

    if interactive:
        return ask_output_path(value or DEFAULT_OUTPUT_PATH)

    return value or DEFAULT_OUTPUT_PATH


def resolve_templates_path(
    value: Path | None,
    *,
    language: str,
    interactive: bool,
) -> Path | None:
    """Resolve templates path."""

    if interactive:
        return ask_templates_path(language)

    return value


def resolve_template_package_path(value: Path | None, *, interactive: bool) -> Path:
    """Resolve template package path."""

    if interactive:
        return ask_template_package_path(value or DEFAULT_TEMPLATE_PACKAGE_PATH)

    return value or DEFAULT_TEMPLATE_PACKAGE_PATH


def resolve_only(value: str | None, *, interactive: bool) -> tuple[str, ...]:
    """Resolve group filter."""

    if interactive:
        prompted = ask_only_groups()
        if prompted:
            return prompted

    return parse_only(value)


def resolve_select(
    value: str | None,
    *,
    interactive: bool,
    required: bool = False,
) -> str | None:
    """Resolve selection filter."""

    if interactive:
        prompted = ask_select(optional=not required)
        if prompted:
            return prompted

    if required and not value:
        raise ValueError("Missing required option: --select")

    return value


def resolve_template_ids(
    template: tuple[str, ...] | list[str] | None,
    only: str | None,
    *,
    interactive: bool,
) -> tuple[str, ...]:
    """Resolve template ID filters from --template, --only, and prompts."""

    values = tuple(template or ()) + parse_csv(only)
    if interactive:
        prompted = ask_template_ids()
        if prompted:
            return values + prompted
    return values


def resolve_strict(value: bool, *, interactive: bool) -> bool:
    """Resolve strict validation flag."""

    if interactive:
        return ask_strict(value)

    return value


def resolve_dry_run(value: bool, *, interactive: bool) -> bool:
    """Resolve dry-run flag."""

    if interactive:
        return ask_dry_run(value)

    return value


def resolve_force(value: bool, *, interactive: bool) -> bool:
    """Resolve force flag."""

    if interactive:
        return ask_force(value)

    return value


def resolve_show_paths(value: bool, *, interactive: bool) -> bool:
    """Resolve show-paths flag."""

    if interactive:
        return ask_show_paths(value)
    return value


def resolve_show_context(value: bool, *, interactive: bool) -> bool:
    """Resolve show-context flag."""

    if interactive:
        return ask_show_context(value)
    return value


def resolve_show_imports(value: bool, *, interactive: bool) -> bool:
    """Resolve show-imports flag."""

    if interactive:
        return ask_show_imports(value)
    return value


def resolve_show_dependencies(value: bool, *, interactive: bool) -> bool:
    """Resolve show-dependencies flag."""

    if interactive:
        return ask_show_dependencies(value)
    return value


def resolve_format(value: bool, *, interactive: bool) -> bool:
    """Resolve format flag."""

    if interactive:
        return ask_format(value)
    return value


def resolve_run_hooks(value: bool, *, interactive: bool) -> bool:
    """Resolve run-hooks flag."""

    if interactive:
        return ask_run_hooks(value)
    return value


def resolve_skip_static(value: bool, *, interactive: bool) -> bool:
    """Resolve skip-static flag."""

    if interactive:
        return ask_skip_static(value)
    return value


def resolve_inspect_mode(interactive: bool) -> str | None:
    """Resolve optional interactive inspect mode."""

    if interactive:
        return ask_inspect_mode()
    return None

"""Shared CLI option annotations."""


SpecPathArg = Annotated[
    Path,
    typer.Argument(help="Path to compiled Codepot spec."),
]

TemplatePackageOption = Annotated[
    Path,
    typer.Option(
        "--template-package",
        "-t",
        help="Path to template package folder or codepotx config file.",
    ),
]

OutputPathOption = Annotated[
    Path,
    typer.Option("--output", "-o", help="Output directory."),
]

LanguageOption = Annotated[
    str | None,
    typer.Option("--language", "-l", help="Override template package language."),
]

SelectOption = Annotated[
    list[str],
    typer.Option("--select", help="Only run templates matching this select expression."),
]

TemplateIdsOption = Annotated[
    list[str],
    typer.Option("--template", help="Only run specific template ids."),
]

DryRunOption = Annotated[
    bool,
    typer.Option("--dry-run", help="Plan writes without writing files."),
]

DebugOption = Annotated[
    bool,
    typer.Option("--debug", help="Enable debug output."),
]

VerboseOption = Annotated[
    bool,
    typer.Option("--verbose", "-v", help="Verbose output."),
]

NoRenderOption = Annotated[
    bool,
    typer.Option("--no-render", help="Skip rendering."),
]

NoWriteOption = Annotated[
    bool,
    typer.Option("--no-write", help="Skip file writing."),
]

NoGraphOption = Annotated[
    bool,
    typer.Option("--no-graph", help="Skip emission graph artifact."),
]

InspectModeOption = Annotated[
    str,
    typer.Option("--mode", "-m", help="Inspection mode."),
]

DEFAULT_TEMPLATE_PACKAGE_OPTION = DEFAULT_TEMPLATE_PACKAGE_PATH
DEFAULT_OUTPUT_OPTION = DEFAULT_OUTPUT_PATH