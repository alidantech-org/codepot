"""Route definition models for compiled Codepot IR resources."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from archives.codepot.src.spec.ir.security.definition import SecurityPolicyDefinition
from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from archives.codepot.src.spec.kinds.routes import HttpMethod

RouteSchemaRef = Ref[Any]


class RouteBodyDefinition(DefinitionItem):
    """Compiled route request body definition."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    schema_: RouteSchemaRef = Field(alias="schema")
    content_type: Ref[Any]
    content_types: tuple[Ref[Any], ...] | None = None


class RouteOutputDefinition(DefinitionItem):
    """Compiled route success output definition."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    status: int
    schema_: RouteSchemaRef | None = Field(default=None, alias="schema")
    content_type: Ref[Any] | None = None


class RouteInlineResponseDefinition(DefinitionItem):
    """Inline route response definition."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    status: int | None = None
    schema_: RouteSchemaRef | None = Field(default=None, alias="schema")
    content_type: Ref[Any] | None = None
    content_types: tuple[Ref[Any], ...] | None = None
    headers: dict[str, RouteSchemaRef] | None = None


RouteResponseDefinition = Ref[Any] | RouteInlineResponseDefinition


class RouteMethodDefinition(DefinitionItem):
    """Compiled route method binding."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: Ref[Any]
    security: Ref[Any] | SecurityPolicyDefinition | None = None

    params: Ref[Any] | None = None
    query: RouteSchemaRef | None = None
    body: RouteBodyDefinition | None = None

    responses: dict[int, RouteResponseDefinition]


class RoutePathDefinition(DefinitionItem):
    """Compiled route path definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    parameters: dict[str, Ref[Any]] | None = None
    methods: dict[HttpMethod, RouteMethodDefinition]


RoutesDefinition = dict[str, RoutePathDefinition]
