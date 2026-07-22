"""Template descriptor models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contracts.paths import PathToken, PathTokenKind
from emission.templates.path_tokens import PathSegment, parse_path_segments


@dataclass(frozen=True)
class TemplateDescriptor:
    """A discovered template file."""

    template_root: Path
    relative_path: Path
    folders: tuple[PathToken, ...] = ()
    output_parts: tuple[str, ...] = ()
    segments: tuple[PathSegment, ...] = ()
    is_template: bool = False


def describe_template(template_root: Path, relative_path: Path) -> TemplateDescriptor:
    """Build a descriptor from a relative template path."""
    segments = parse_path_segments(tuple(relative_path.parts))
    folders = _folder_tokens(segments)

    if len(folders) > 1:
        names = ", ".join(token.expression for token in folders)
        raise ValueError(f"template paths may contain only one folder recipe token: {names}")

    return TemplateDescriptor(
        template_root=template_root,
        relative_path=relative_path,
        folders=folders,
        output_parts=_output_parts(segments),
        segments=segments,
        is_template=relative_path.as_posix().endswith(".j2"),
    )


def _folder_tokens(segments: tuple[PathSegment, ...]) -> tuple[PathToken, ...]:
    folders: list[PathToken] = []

    for segment in segments:
        if not segment.is_folder or not segment.tokens:
            continue

        token = segment.tokens[0]
        if token.kind == PathTokenKind.FOLDER:
            folders.append(token)

    return tuple(folders)


def _output_parts(segments: tuple[PathSegment, ...]) -> tuple[str, ...]:
    """Return path parts excluding folder recipe tokens."""
    return tuple(segment.raw for segment in segments if not segment.is_folder)
