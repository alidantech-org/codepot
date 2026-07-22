"""Root response registry models for compiled Codepot IR."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from archives.codepot.src.spec.ir.response.errors.definition import ErrorResponseDefinition


class ResponsesDefinition(BaseModel):
    """Compiled reusable response registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    errors: dict[str, ErrorResponseDefinition]
