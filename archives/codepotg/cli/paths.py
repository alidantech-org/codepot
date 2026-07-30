"""CLI path normalization helpers."""

from __future__ import annotations

import re
from pathlib import Path

_MSYS_DRIVE_PATH = re.compile(r"^[\\/](?P<drive>[A-Za-z])(?:[\\/](?P<rest>.*))?$")


def normalize_cli_path(value: Path | str | None) -> Path | None:
    """Normalize shell-specific path forms before app workflows receive them."""
    if value is None:
        return None

    text = str(value)
    match = _MSYS_DRIVE_PATH.match(text)

    if match:
        drive = match.group("drive").upper()
        rest = (match.group("rest") or "").replace("/", "\\")
        return Path(f"{drive}:\\{rest}" if rest else f"{drive}:\\")

    return Path(value)
