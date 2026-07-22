"""Template scanner."""

from __future__ import annotations

from pathlib import Path

from emission.templates.descriptor import TemplateDescriptor, describe_template

PATH_CONFIG_FILE = "paths.yaml"


def scan_templates(template_root: Path) -> tuple[TemplateDescriptor, ...]:
    """Scan a template root and return descriptors for all emitted files."""
    if not template_root.exists():
        raise FileNotFoundError(f"Template root not found: {template_root}")

    descriptors: list[TemplateDescriptor] = []

    for path in sorted(template_root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(template_root)

        if relative_path.as_posix() == PATH_CONFIG_FILE:
            continue

        if any(part.startswith("_") for part in relative_path.parts):
            continue

        descriptors.append(describe_template(template_root, relative_path))

    return tuple(descriptors)
