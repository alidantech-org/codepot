"""Metadata contracts for normalized spec context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from archives.codepot.src.contracts.spec.refs import SpecRef


@dataclass(frozen=True)
class SpecDefinitionMeta:
    """Common metadata from definition items."""

    description: str | None = None
    deprecated: bool = False
    meta: dict[str, Any] | None = None
    ownership: SpecRef | None = None


@dataclass(frozen=True)
class SpecFileMetadata:
    """Source file metadata for the loaded compiled spec."""

    path: Path
    size_bytes: int
    size_label: str
    line_count: int


@dataclass(frozen=True)
class SpecProjectMetadata:
    """Project/API metadata from the compiled spec root."""

    codepot_version: str
    project_key: str
    spec_version: int
    title: str
    version: str
    summary: str | None
    terms_of_service: str | None


@dataclass(frozen=True)
class SpecContact:
    """Normalized API contact metadata."""

    name: str | None
    url: str | None
    email: str | None


@dataclass(frozen=True)
class SpecLicense:
    """Normalized API license metadata."""

    name: str
    identifier: str | None
    url: str | None


@dataclass(frozen=True)
class SpecInfoLinks:
    """Normalized project information links."""

    website: str | None
    docs: str | None
    support: str | None
    changelog: str | None
    status: str | None
    repository: str | None


@dataclass(frozen=True)
class SpecMetadata:
    """Complete normalized metadata for a compiled spec."""

    file: SpecFileMetadata
    project: SpecProjectMetadata
    contact: SpecContact | None
    license: SpecLicense | None
    links: SpecInfoLinks | None
