"""Template fixture helpers."""

from __future__ import annotations

from pathlib import Path


def write_debug_templates(root: Path) -> Path:
    """Create a minimal debug template tree with folder recipe paths."""
    template_root = root / "debug"
    (template_root / "{resource}").mkdir(parents=True)
    (template_root / "{model}").mkdir(parents=True)

    # Write paths.yaml configuration
    (template_root / "paths.yaml").write_text(
        """template_extension: ".j2"
strip_template_extension: true
allow_raw_files: true

folders:
  resource:
    select: resources
    as: resource
    parts:
      - docs
      - resources
      - [resource.emit.resource_path]

  model:
    select: schemas.emit_models
    as: model
    parts:
      - docs
      - resources
      - [model.emit.resource_path]
      - schemas
      - models
""",
        encoding="utf-8",
    )

    (template_root / "summary.txt.j2").write_text(
        "API: {{ api.info.title }}\nLanguage: {{ lang.name }}\n",
        encoding="utf-8",
    )
    (template_root / "{resource}" / "index.md.j2").write_text(
        "Resource: {{ resource.name.pascal.o }}\n",
        encoding="utf-8",
    )
    (template_root / "{resource}" / "operations.md.j2").write_text(
        "Operations: {{ resource.operations | length }}\n",
        encoding="utf-8",
    )
    (template_root / "{resource}" / "schemas.md.j2").write_text(
        "Schemas: {{ resource.schemas | length }}\n",
        encoding="utf-8",
    )
    (template_root / "{model}" / "[model.name.path.o].md.j2").write_text(
        "Schema: {{ model.name.pascal.o }}\nKind: {{ model.api.kind }}\n",
        encoding="utf-8",
    )
    (template_root / ".gitignore").write_text(
        "*.tmp\n",
        encoding="utf-8",
    )

    return template_root
