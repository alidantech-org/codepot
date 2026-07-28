"""Path-safe values for debug template context objects."""

from __future__ import annotations


def safe_path_parts(value: object, *, fallback: str = "shared") -> tuple[str, ...]:
    if value is None:
        return (fallback,)

    if isinstance(value, list | tuple):
        parts = [str(part).strip() for part in value if str(part).strip()]
    else:
        text = str(value).replace("\\", "/").strip()
        parts = [part.strip() for part in text.split("/") if part.strip()]

    cleaned = tuple(part for part in parts if part not in {".", ".."})

    return cleaned or (fallback,)


def safe_file_name(value: object, *, fallback: str = "item") -> str:
    parts = safe_path_parts(value, fallback=fallback)
    return "_".join(parts)
