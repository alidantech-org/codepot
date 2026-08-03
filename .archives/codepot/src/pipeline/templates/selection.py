"""Template selection parsing and validation."""

from __future__ import annotations

from archives.codepot.src.contracts.templates.config.selection import (
    TemplateSelect,
    TemplateSelectMode,
    TemplateSelectSubject,
)


def parse_template_select(value: str) -> TemplateSelect:
    """Parse a template select expression."""

    if value == TemplateSelectMode.ONCE.value:
        return TemplateSelect(
            raw=value,
            subject=None,
            mode=TemplateSelectMode.ONCE,
        )

    parts = value.split(".")

    if len(parts) != 2:
        raise ValueError(
            "Invalid template select expression. Expected 'once' or '<subject>.<mode>', "
            f"got: {value}"
        )

    subject_value, mode_value = parts

    try:
        subject = TemplateSelectSubject(subject_value)
    except ValueError as error:
        raise ValueError(f"Unsupported template select subject: {subject_value}") from error

    try:
        mode = TemplateSelectMode(mode_value)
    except ValueError as error:
        raise ValueError(
            "Unsupported template select mode. Use one of: once, each, all, by_owner. "
            f"Got: {mode_value}"
        ) from error

    return TemplateSelect(
        raw=value,
        subject=subject,
        mode=mode,
    )


def validate_template_select(value: str) -> TemplateSelect:
    """Validate and return parsed template select expression."""

    selected = parse_template_select(value)

    if selected.mode == TemplateSelectMode.ONCE and selected.subject is not None:
        raise ValueError("Select mode 'once' must not have a subject.")

    if selected.mode != TemplateSelectMode.ONCE and selected.subject is None:
        raise ValueError(f"Select expression requires a subject: {value}")

    return selected