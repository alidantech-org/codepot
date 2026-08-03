"""Info section models for compiled Codepot IR."""

from __future__ import annotations

from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from pydantic import ConfigDict


class ContactDefinition(DefinitionItem):
    """Product/API contact information."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str | None = None
    url: str | None = None
    email: str | None = None


class LicenseDefinition(DefinitionItem):
    """Product/API license information."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    identifier: str | None = None
    url: str | None = None


class InfoLinksDefinition(DefinitionItem):
    """Useful product/project links."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    website: str | None = None
    docs: str | None = None
    support: str | None = None
    changelog: str | None = None
    status: str | None = None
    repository: str | None = None


class InfoDefinition(DefinitionItem):
    """Compiled Codepot API/product information."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str
    version: str
    summary: str | None = None
    terms_of_service: str | None = None
    contact: ContactDefinition | None = None
    license: LicenseDefinition | None = None
    links: InfoLinksDefinition | None = None
