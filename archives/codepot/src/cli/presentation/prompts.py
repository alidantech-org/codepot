"""Interactive CLI prompts."""

from __future__ import annotations

from pathlib import Path

import questionary

from archives.codepot.src.cli.constants.defaults import (
    DEFAULT_LANGUAGE,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SPEC_PATH,
    DEFAULT_TEMPLATE_PACKAGE_PATH,
    DEFAULT_TEMPLATES_ROOT,
)


def ask_spec_path(default: Path = DEFAULT_SPEC_PATH) -> Path:
    """Ask for the spec path."""

    value = questionary.path("Spec path:", default=str(default)).ask()
    return Path(value or default)


def ask_language(default: str = DEFAULT_LANGUAGE) -> str:
    """Ask for target language."""

    value = questionary.text("Target language:", default=default).ask()
    return value or default


def ask_templates_path(language: str, default_root: Path = DEFAULT_TEMPLATES_ROOT) -> Path:
    """Ask for templates directory."""

    default = default_root / language
    value = questionary.path("Templates directory:", default=str(default)).ask()
    return Path(value or default)


def ask_template_package_path(default: Path = DEFAULT_TEMPLATE_PACKAGE_PATH) -> Path:
    """Ask for template package directory."""

    value = questionary.path("Template package path:", default=str(default)).ask()
    return Path(value or default)


def ask_output_path(default: Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Ask for output root."""

    value = questionary.path("Output root:", default=str(default)).ask()
    return Path(value or default)


def ask_only_groups() -> tuple[str, ...]:
    """Ask for optional group IDs."""

    value = questionary.text("Only groups, comma-separated:", default="").ask()
    if not value:
        return ()

    return tuple(part.strip() for part in value.split(",") if part.strip())


def ask_select(optional: bool = True) -> str | None:
    """Ask for a selection filter."""

    value = questionary.text("Selection filter:", default="").ask()
    if value:
        return value
    return None if optional else ""


def ask_template_ids() -> tuple[str, ...]:
    """Ask for template IDs."""

    value = questionary.text("Template IDs, comma-separated:", default="").ask()
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def ask_inspect_mode() -> str:
    """Ask for inspect mode."""

    value = questionary.select(
        "Inspect mode:",
        choices=["overview", "schemas", "resources", "content_types", "refs"],
        default="overview",
    ).ask()
    return str(value or "overview")


def ask_show_paths(default: bool = False) -> bool:
    """Ask whether output should show paths only."""

    return bool(questionary.confirm("Show paths only?", default=default).ask())


def ask_show_context(default: bool = False) -> bool:
    """Ask whether output should show context previews."""

    return bool(questionary.confirm("Show context?", default=default).ask())


def ask_show_imports(default: bool = False) -> bool:
    """Ask whether output should show imports."""

    return bool(questionary.confirm("Show imports?", default=default).ask())


def ask_show_dependencies(default: bool = False) -> bool:
    """Ask whether output should show dependencies."""

    return bool(questionary.confirm("Show dependencies?", default=default).ask())


def ask_dry_run(default: bool = False) -> bool:
    """Ask whether this should be a dry run."""

    value = questionary.confirm("Dry run?", default=default).ask()
    return bool(value)


def ask_force(default: bool = False) -> bool:
    """Ask whether files should be overwritten."""

    value = questionary.confirm("Force overwrite?", default=default).ask()
    return bool(value)


def ask_format(default: bool = False) -> bool:
    """Ask whether formatting should run."""

    return bool(questionary.confirm("Format after emit?", default=default).ask())


def ask_run_hooks(default: bool = False) -> bool:
    """Ask whether hooks should run."""

    return bool(questionary.confirm("Run hooks after emit?", default=default).ask())


def ask_skip_static(default: bool = False) -> bool:
    """Ask whether static files should be skipped."""

    return bool(questionary.confirm("Skip static files?", default=default).ask())


def ask_strict(default: bool = False) -> bool:
    """Ask whether strict validation should be enabled."""

    value = questionary.confirm("Strict validation?", default=default).ask()
    return bool(value)
