"""Error response definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref


class ErrorResponseDefinition(DefinitionItem):
    """Reusable typed error response definition."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    status: int
    intent: str | None = None
    schema_: Ref[Any] = Field(alias="schema")
    content_type: Ref[Any]
    content_types: list[Ref[Any]] | None = None
    headers: dict[str, Ref[Any]] | None = None
