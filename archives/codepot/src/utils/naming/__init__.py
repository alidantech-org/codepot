"""Unified naming utilities for generator contexts.

Access pattern: case-first, plurality-second.

    name.snake              → "upload_avatar"
    name.singular.snake     → "upload_avatar"
    name.plural.snake       → "upload_avatars"
    name.pascal             → "UploadAvatar"
    name.plural.pascal      → "UploadAvatars"

Short aliases are also supported:

    name.sn  → name.snake
    name.pc  → name.pascal
    name.cm  → name.camel
"""

from archives.codepot.src.contracts.spec.names import (
    SpecName,
    SpecNameCase,
    SpecNameCases,
    resolve_name_case,
)
from archives.codepot.src.utils.naming.provider import NameProvider, build_name

__all__ = [
    "NameProvider",
    "build_name",
    "SpecName",
    "SpecNameCases",
    "SpecNameCase",
    "resolve_name_case",
]
