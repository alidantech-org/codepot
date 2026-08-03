"""Template scanner."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.emission.paths.config_loader import PATH_CONFIG_FILES
from archives.codepotg.src.emission.templates.descriptor import (
    TemplateDescriptor,
    describe_template,
)
from archives.codepotg.src.emission.templates.renderer import clear_environment_cache


def scan_templates(template_root: Path) -> tuple[TemplateDescriptor, ...]:
    """Scan a template root and return descriptors for all emitted files.

    A scan marks the start of a new emission plan. Clear compiled Jinja state once
    here so template edits made between separate emissions are observed, while all
    files inside the current emission still share one compiled environment cache.
    """
    if not template_root.exists():
        raise FileNotFoundError(f"Template root not found: {template_root}")

    clear_environment_cache()
    descriptors: list[TemplateDescriptor] = []

    for path in sorted(template_root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(template_root)

        if relative_path.as_posix() in PATH_CONFIG_FILES:
            continue

        if any(part.startswith("_") for part in relative_path.parts):
            continue

        descriptors.append(describe_template(template_root, relative_path))

    return tuple(descriptors)
