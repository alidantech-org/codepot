"""Jinja template rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.planning.contexts import (
    PlannedTemplateContexts,
    TemplateFileContext,
)
from jinja2 import Environment, FileSystemLoader, StrictUndefined


@dataclass(frozen=True)
class RenderedFile:
    """One rendered output file."""

    file_id: str
    output_path: Path
    relative_output_path: str
    content: str
    source_path: Path | None = None
    is_static: bool = False


@dataclass(frozen=True)
class RenderedFiles:
    """All rendered/copied files."""

    files: tuple[RenderedFile, ...]


def _template_context(context: TemplateFileContext) -> dict[str, object]:
    """Build shallow Jinja context for one planned template file."""

    return {
        "file": context,
        "template": context.template,
        "language": context.language,
        "spec": context.spec,
        "project": context.spec.metadata.project,
        "records": context.records,
        "imports": context.imports,
        "exports": context.exports,
    }


def create_environment(package_path: Path) -> Environment:
    """Create a strict Jinja environment for a template package."""

    return Environment(
        loader=FileSystemLoader(package_path),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_static_file(context: TemplateFileContext) -> RenderedFile:
    """Return a static file copy plan."""

    if context.source_template_path is None:
        raise ValueError(f"Static file has no source path: {context.file_id}")

    return RenderedFile(
        file_id=context.file_id,
        output_path=context.output_path,
        relative_output_path=context.relative_output_path,
        content="",
        source_path=context.source_template_path,
        is_static=True,
    )


def render_template_file(
    *,
    environment: Environment,
    context: TemplateFileContext,
) -> RenderedFile:
    """Render one planned template file."""

    if context.is_static:
        return render_static_file(context)

    if context.template_file is None:
        raise ValueError(f"Template file is missing: {context.file_id}")

    template = environment.get_template(context.template_file)
    content = template.render(_template_context(context))

    return RenderedFile(
        file_id=context.file_id,
        output_path=context.output_path,
        relative_output_path=context.relative_output_path,
        content=content,
        source_path=context.source_template_path,
        is_static=False,
    )


def render_template_contexts(
    *,
    package_path: Path,
    contexts: PlannedTemplateContexts,
) -> RenderedFiles:
    """Render all planned template contexts."""

    environment = create_environment(package_path)

    return RenderedFiles(
        files=tuple(
            render_template_file(
                environment=environment,
                context=context,
            )
            for context in contexts.files
        )
    )