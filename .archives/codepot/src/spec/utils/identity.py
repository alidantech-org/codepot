"""Controlled dot-identity parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.spec.utils.constants import IDENTITY_SEPARATOR


@dataclass(frozen=True)
class ParsedIdentity:
    """Parsed identity metadata from a compiled key."""

    raw: str
    local_key: str
    owner_identity: str | None = None
    owner_key: str | None = None
    owner_path: tuple[str, ...] = ()


def parse_identity(raw: str) -> ParsedIdentity:
    """Parse a dot-identity key.

    Dot notation is identity metadata, not a filesystem path.

    Supported shapes:
    - local
    - owner_identity.owner_key.local
    - owner_identity.owner_key.nested.local

    The final local key is always the last part.
    The owner key is always the second part.
    Any middle parts after owner key are retained as owner_path metadata.
    """

    parts = tuple(part for part in raw.split(IDENTITY_SEPARATOR) if part)

    if len(parts) < 3:
        return ParsedIdentity(raw=raw, local_key=raw)

    return ParsedIdentity(
        raw=raw,
        owner_identity=parts[0],
        owner_key=parts[1],
        owner_path=parts[2:-1],
        local_key=parts[-1],
    )


def has_owner_identity(identity: ParsedIdentity) -> bool:
    """Return true when parsed identity contains owner metadata."""

    return identity.owner_identity is not None and identity.owner_key is not None
