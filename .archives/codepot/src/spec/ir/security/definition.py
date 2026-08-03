"""Security definition models for compiled Codepot IR."""

from __future__ import annotations

from typing import Any

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.ref import Ref
from archives.codepot.src.spec.kinds.security import (
    SecurityCredentialFormat,
    SecurityCredentialSource,
    SecurityPolicyMode,
)
from pydantic import BaseModel, ConfigDict


class SecurityCredentialDefinition(DefinitionItem):
    """Credential extraction definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: SecurityCredentialSource
    key: str
    format: SecurityCredentialFormat | None = None
    value_type: Ref[Any] | None = None


SecurityPrincipalFields = dict[str, Ref[Any]]


class SecurityPrincipalDefinition(DefinitionItem):
    """Typed authenticated principal definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fields: SecurityPrincipalFields


class SecurityPolicyDefinition(DefinitionItem):
    """Compiled route/resource security policy."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: SecurityPolicyMode
    credential: Ref[Any] | None = None
    principals: dict[str, Ref[Any]] | None = None
    roles: list[str] | None = None
    permissions: list[str] | None = None
    intent: str | None = None


class SecurityDefinition(BaseModel):
    """Compiled security registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    credentials: dict[str, SecurityCredentialDefinition]
    principals: dict[str, SecurityPrincipalDefinition]
    policies: dict[str, SecurityPolicyDefinition]
