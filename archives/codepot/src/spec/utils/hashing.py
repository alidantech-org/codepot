"""Deterministic hashing helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final

from archives.codepot.src.spec.utils.constants import HASH_ALGORITHM, HASH_JSON_ENCODING

_CHUNK_SIZE: Final[int] = 1024 * 1024


def hash_text(value: str) -> str:
    """Hash text using the repository hash algorithm."""

    return hashlib.new(
        HASH_ALGORITHM,
        value.encode(HASH_JSON_ENCODING),
    ).hexdigest()


def hash_bytes(value: bytes) -> str:
    """Hash bytes using the repository hash algorithm."""

    return hashlib.new(HASH_ALGORITHM, value).hexdigest()


def hash_file(path: Path) -> str:
    """Hash file contents in chunks."""

    digest = hashlib.new(HASH_ALGORITHM)

    with path.open("rb") as file:
        while chunk := file.read(_CHUNK_SIZE):
            digest.update(chunk)

    return digest.hexdigest()
