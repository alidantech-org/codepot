"""Template variable listing contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TemplateVariableKind(StrEnum):
    """Kinds of variables exposed to users."""

    OUTPUT_PATH = "output_path"
    TEMPLATE_CONTEXT = "template_context"


@dataclass(frozen=True)
class TemplateVariable:
    """One documented template variable."""

    path: str
    description: str
    kind: TemplateVariableKind
    required: bool = False
    example: str | None = None


@dataclass(frozen=True)
class TemplateVariableSection:
    """A named group of template variables."""

    title: str
    variables: tuple[TemplateVariable, ...]


@dataclass(frozen=True)
class TemplateVariableCatalog:
    """All variables available for one selection."""

    select: str
    output_path: tuple[TemplateVariableSection, ...]
    template_context: tuple[TemplateVariableSection, ...]