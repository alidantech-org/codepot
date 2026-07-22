"""Operation definition models for compiled Codepot IR resources."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref

OperationSchemaRef = Ref[Any]
OperationContextRef = Ref[Any]


class OperationInputDefinition(DefinitionItem):
    """Compiled operation input schema refs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context: list[OperationContextRef] | None = None
    params: Ref[Any] | None = None
    query: OperationSchemaRef | None = None
    body: OperationSchemaRef | None = None


class OperationOutputDefinition(DefinitionItem):
    """Compiled operation output schema refs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    result: OperationSchemaRef | None = None
    errors: list[Ref[Any]] | None = None


class OperationDefinition(DefinitionItem):
    """Compiled resource operation definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    input: OperationInputDefinition
    output: OperationOutputDefinition
