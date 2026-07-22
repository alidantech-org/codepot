"""Spec repository metadata builder."""

from __future__ import annotations

from pathlib import Path

from archives.codepot.src.contracts.spec.context import (
    SpecContactMetadata,
    SpecFileMetadata,
    SpecInfoLinksMetadata,
    SpecLicenseMetadata,
    SpecMetadata,
    SpecProjectMetadata,
)
from archives.codepot.src.spec.ir.shared.document import CodepotDefinition
from archives.codepot.src.spec.utils.hashing import hash_file
from archives.codepot.src.spec.utils.paths import count_file_lines, file_size_label


def build_file_metadata(path: Path) -> SpecFileMetadata:
    """Build source file metadata."""

    size = path.stat().st_size

    return SpecFileMetadata(
        path=path,
        size_bytes=size,
        size_label=file_size_label(size),
        line_count=count_file_lines(path),
        hash=hash_file(path),
    )


def build_project_metadata(document: CodepotDefinition) -> SpecProjectMetadata:
    """Build project metadata from a typed Codepot document."""

    return SpecProjectMetadata(
        codepot_version=document.codepot,
        project_key=document.key,
        project_version=document.info.version,
        title=document.info.title,
        summary=document.info.summary,
        version=document.version,
        terms_of_service=document.info.terms_of_service,
    )


def build_contact_metadata(document: CodepotDefinition) -> SpecContactMetadata | None:
    """Build contact metadata when available."""

    contact = document.info.contact

    if contact is None:
        return None

    return SpecContactMetadata(
        name=contact.name,
        url=contact.url,
        email=contact.email,
    )


def build_license_metadata(document: CodepotDefinition) -> SpecLicenseMetadata | None:
    """Build license metadata when available."""

    license_info = document.info.license

    if license_info is None:
        return None

    return SpecLicenseMetadata(
        name=license_info.name,
        identifier=license_info.identifier,
        url=license_info.url,
    )


def build_links_metadata(document: CodepotDefinition) -> SpecInfoLinksMetadata | None:
    """Build info links metadata when available."""

    links = document.info.links

    if links is None:
        return None

    return SpecInfoLinksMetadata(
        website=links.website,
        docs=links.docs,
        support=links.support,
        changelog=links.changelog,
        status=links.status,
        repository=links.repository,
    )


def build_metadata(path: Path, document: CodepotDefinition) -> SpecMetadata:
    """Build complete normalized spec metadata."""

    return SpecMetadata(
        file=build_file_metadata(path),
        project=build_project_metadata(document),
        contact=build_contact_metadata(document),
        license=build_license_metadata(document),
        links=build_links_metadata(document),
    )
