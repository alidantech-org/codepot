"""Changed-aware atomic file writing for emission."""

from __future__ import annotations

import os
import uuid
from contextlib import suppress
from pathlib import Path

from archives.codepotg.src.contracts.emission import EmissionWriteResult


def write_text_if_changed(
    path: Path,
    content: str,
    *,
    compare_mode: str = "exact",
) -> EmissionWriteResult:
    """Atomically write normalized UTF-8 text only when content changed."""

    normalized = content.rstrip("\n") + "\n" if content else ""
    encoded = normalized.encode("utf-8")

    if not path.exists():
        _atomic_write(path, encoded)
        return EmissionWriteResult(created=(path,))

    existing = path.read_text(encoding="utf-8")
    if _text_changed(existing, normalized, compare_mode=compare_mode):
        _atomic_write(path, encoded)
        return EmissionWriteResult(updated=(path,))

    return EmissionWriteResult(unchanged=(path,))


def write_bytes_if_changed(path: Path, content: bytes) -> EmissionWriteResult:
    """Atomically write raw bytes only when content changed."""

    if path.exists():
        if path.read_bytes() == content:
            return EmissionWriteResult(unchanged=(path,))
        _atomic_write(path, content)
        return EmissionWriteResult(updated=(path,))

    _atomic_write(path, content)
    return EmissionWriteResult(created=(path,))


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        with suppress(OSError):
            temporary.unlink()
        raise


def _text_changed(old: str, new: str, *, compare_mode: str = "exact") -> bool:
    """Check if text changed based on comparison mode."""

    old_normalized = _normalize_newlines(old)
    new_normalized = _normalize_newlines(new)

    if compare_mode == "layout_insensitive":
        return _layout_key(old_normalized) != _layout_key(new_normalized)

    return _ensure_final_newline(old_normalized) != _ensure_final_newline(new_normalized)


def _layout_key(value: str) -> str:
    """Remove whitespace outside quoted strings for layout-insensitive comparison."""

    result: list[str] = []
    in_string = False
    quote = ""
    escaped = False

    for char in value:
        if in_string:
            result.append(char)

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == quote:
                in_string = False
                quote = ""

            continue

        if char in ("'", '"'):
            in_string = True
            quote = char
            result.append(char)
            continue

        if char.isspace():
            continue

        result.append(char)

    return "".join(result)


def _normalize_newlines(value: str) -> str:
    """Normalize line endings to \n."""

    return value.replace("\r\n", "\n").replace("\r", "\n")


def _ensure_final_newline(value: str) -> str:
    """Ensure text ends with single newline."""

    return value.rstrip("\n") + "\n" if value else ""
