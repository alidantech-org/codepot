"""Content type models for compiled Codepot IR."""

from __future__ import annotations

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.kinds.content import ContentStrategy
from pydantic import ConfigDict


class ContentTypeDefinition(DefinitionItem):
    """Reusable content type definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str
    strategy: ContentStrategy
    binary: bool | None = None
    structured: bool | None = None
