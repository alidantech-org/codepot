"""Once-selection template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext


@dataclass(frozen=True)
class TemplateOnceContext:
    """Context for ``select: once`` templates.

    Once templates receive only base context by default. They do not receive
    item, owner, resource, or collection context unless a future explicit
    context/include option adds it.
    """

    base: TemplateBaseContext
