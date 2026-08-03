"""Spec repository path helpers."""

from __future__ import annotations

from pathlib import Path


def file_size_label(size_bytes: int) -> str:
    """Return a human-friendly file size label."""

    if size_bytes < 1024:
        return f"{size_bytes} B"

    kib = size_bytes / 1024
    if kib < 1024:
        return f"{kib:.1f} KiB"

    mib = kib / 1024
    if mib < 1024:
        return f"{mib:.1f} MiB"

    gib = mib / 1024
    return f"{gib:.1f} GiB"


def count_file_lines(path: Path) -> int:
    """Count lines in a text file."""

    with path.open("r", encoding="utf-8") as file:
        return sum(1 for _line in file)


def read_file_bytes(path: Path) -> bytes:
    """Read file bytes."""

    return path.read_bytes()
