"""Shared base definition models for Codepot IR items."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from archives.codepot.src.spec.ir.shared.ref import Ref


class DefinitionItem(BaseModel):
    """Base metadata available on most compiled Codepot IR items."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    meta: dict[str, Any] | None = None
    description: str | None = None
    deprecated: bool | None = None
    ownership: Ref[Any] | None = None
