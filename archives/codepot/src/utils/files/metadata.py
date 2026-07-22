"""File metadata helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileMetadata:
    """Basic metadata for a loaded source file."""

    path: Path
    size_bytes: int
    size_label: str
    line_count: int


def get_file_metadata(path: Path) -> FileMetadata:
    """Return file size and line count for a UTF-8 text file."""

    size_bytes = path.stat().st_size
    with path.open("r", encoding="utf-8") as file:
        line_count = sum(1 for _ in file)

    return FileMetadata(
        path=path,
        size_bytes=size_bytes,
        size_label=format_bytes(size_bytes),
        line_count=line_count,
    )


def format_bytes(size_bytes: int) -> str:
    """Format bytes as a compact human-readable value."""

    units = ("B", "KB", "MB", "GB")
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} {units[-1]}"
