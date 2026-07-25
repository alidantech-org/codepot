"""Root response registry models for compiled Codepot IR."""

from __future__ import annotations

from archives.codepot.src.spec.ir.response.errors.definition import ErrorResponseDefinition
from pydantic import BaseModel, ConfigDict


class ResponsesDefinition(BaseModel):
    """Compiled reusable response registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    errors: dict[str, ErrorResponseDefinition]
