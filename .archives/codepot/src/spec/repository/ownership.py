"""Spec repository ownership helpers."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.refs import SpecIdentity, SpecOwner
from archives.codepot.src.spec.repository.names import create_spec_name
from archives.codepot.src.spec.repository.owner_index import OwnerFolderIndex
from archives.codepot.src.spec.repository.ownership_kinds import owner_subject_from_identity
from archives.codepot.src.spec.repository.refs import create_spec_ref
from archives.codepot.src.spec.utils.constants import GLOBAL_OWNER_KEY
from archives.codepot.src.spec.utils.identity import has_owner_identity, parse_identity


def create_global_owner() -> SpecOwner:
    """Create synthetic global owner."""

    name = create_spec_name(GLOBAL_OWNER_KEY)

    return SpecOwner(
        key=GLOBAL_OWNER_KEY,
        ref=None,
        identity=SpecIdentity(
            raw=GLOBAL_OWNER_KEY,
            local_key=GLOBAL_OWNER_KEY,
            owner_identity=None,
            owner_key=None,
        ),
        name=name,
        folders=(),
        is_global=True,
    )


def create_spec_identity(key: str) -> SpecIdentity:
    """Create normalized spec identity from a compiled key."""

    parsed = parse_identity(key)

    return SpecIdentity(
        raw=parsed.raw,
        local_key=parsed.local_key,
        owner_identity=parsed.owner_identity,
        owner_key=parsed.owner_key,
    )


def create_owner_from_identity(
    *,
    key: str,
    owner_index: OwnerFolderIndex,
) -> SpecOwner:
    """Create owner metadata from identity, or global owner when missing."""

    parsed = parse_identity(key)

    if not has_owner_identity(parsed):
        return create_global_owner()

    if parsed.owner_identity is None or parsed.owner_key is None:
        return create_global_owner()

    owner_subject = owner_subject_from_identity(parsed.owner_identity)

    if owner_subject is None:
        return create_global_owner()

    owner_name = create_spec_name(parsed.owner_key)
    folder_info = owner_index.find(subject=owner_subject, key=parsed.owner_key)

    owner_identity = SpecIdentity(
        raw=parsed.owner_key,
        local_key=parsed.owner_key,
        owner_identity=parsed.owner_identity,
        owner_key=parsed.owner_key,
    )

    return SpecOwner(
        key=parsed.owner_key,
        ref=create_spec_ref(subject=owner_subject, key=parsed.owner_key),
        identity=owner_identity,
        name=owner_name,
        folders=folder_info.folders if folder_info is not None else (),
        is_global=False,
    )
