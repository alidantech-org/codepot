"""Template config ref validation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.templates.config.package import TemplatePackageConfig

REF_PREFIX = "#/"
REF_SEPARATOR = "/"


@dataclass(frozen=True)
class ParsedTemplateRef:
    """Parsed template package ref."""

    template_id: str
    points_to_barrel: bool


def parse_template_ref(value: str) -> ParsedTemplateRef:
    """Parse a template resolver ref.

    Supported:
    - #/templates/models
    - #/templates/models/barrel
    """

    if not value.startswith(REF_PREFIX):
        raise ValueError(f"Template ref must start with {REF_PREFIX}: {value}")

    parts = tuple(
        part for part in value[len(REF_PREFIX) :].split(REF_SEPARATOR) if part
    )

    if len(parts) not in {2, 3}:
        raise ValueError(f"Invalid template ref: {value}")

    section = parts[0]
    template_id = parts[1]

    if section != "templates":
        raise ValueError(f"Template ref must point to templates section: {value}")

    points_to_barrel = len(parts) == 3 and parts[2] == "barrel"

    if len(parts) == 3 and not points_to_barrel:
        raise ValueError(f"Unsupported template ref target: {value}")

    return ParsedTemplateRef(
        template_id=template_id,
        points_to_barrel=points_to_barrel,
    )


def validate_template_ref(
    *,
    value: str,
    config: TemplatePackageConfig,
) -> None:
    """Validate a template resolver ref against package config."""

    parsed = parse_template_ref(value)

    if parsed.template_id not in config.templates:
        raise ValueError(f"Template ref points to unknown template: {value}")

    target = config.templates[parsed.template_id]

    if parsed.points_to_barrel and not target.barrel_enabled:
        raise ValueError(f"Template ref points to disabled barrel: {value}")