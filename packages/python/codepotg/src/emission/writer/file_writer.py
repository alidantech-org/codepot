"""Changed-aware file writing for emission."""

from __future__ import annotations

from pathlib import Path

from contracts.emission import EmissionWriteResult


def write_text_if_changed(
    path: Path,
    content: str,
    *,
    compare_mode: str = "exact",
) -> EmissionWriteResult:
    """Write text to file only if content changed, normalizing final newline.

    Args:
        path: Target file path.
        content: New content to write.
        compare_mode: Comparison mode - "exact", "layout_insensitive", or "raw".

    Returns:
        EmissionWriteResult indicating what happened.
    """
    # Normalize content to end with single newline
    normalized = content.rstrip("\n") + "\n" if content else ""

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(normalized, encoding="utf-8")
        return EmissionWriteResult(created=(path,))

    existing = path.read_text(encoding="utf-8")

    if _text_changed(existing, normalized, compare_mode=compare_mode):
        path.write_text(normalized, encoding="utf-8")
        return EmissionWriteResult(updated=(path,))

    return EmissionWriteResult(unchanged=(path,))


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
    """Normalize line endings to \\n."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _ensure_final_newline(value: str) -> str:
    """Ensure text ends with single newline."""
    return value.rstrip("\n") + "\n" if value else ""
