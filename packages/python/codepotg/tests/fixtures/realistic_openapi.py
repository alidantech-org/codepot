from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

FICTIONAL_API_TITLE = "Northstar Platform API"
FICTIONAL_API_DESCRIPTION = (
    "Large fictional multi-tenant platform API used to validate realistic CodepotG packs."
)
FICTIONAL_SERVER_URL = "https://api.northstar.example/v1"


def write_fictional_real_openapi(source: Path, destination: Path) -> Path:
    """Copy the canonical real fixture while replacing only authored branding values."""
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("Canonical OpenAPI fixture root must be an object")

    sanitized = _sanitize_value(raw)
    if not isinstance(sanitized, dict):
        raise TypeError("Sanitized OpenAPI fixture root must remain an object")

    info = sanitized.setdefault("info", {})
    if not isinstance(info, dict):
        raise TypeError("OpenAPI info must be an object")
    info.update(
        {
            "title": FICTIONAL_API_TITLE,
            "description": FICTIONAL_API_DESCRIPTION,
            "version": "v1",
        }
    )
    sanitized["servers"] = [
        {
            "url": FICTIONAL_SERVER_URL,
            "description": "Fictional production API",
        }
    ]

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            sanitized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    return destination


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return (
            value.replace("Alidantech", "Northstar")
            .replace("ALIDANTECH", "NORTHSTAR")
            .replace("alidantech", "northstar")
            .replace("Sierre Technologies", "Example Technologies")
            .replace("Sierre", "Example")
            .replace("sierre", "example")
            .replace("Riderescue", "Sample Product")
            .replace("RideRescue", "Sample Product")
            .replace("riderescue", "sample-product")
        )
    if isinstance(value, Mapping):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_sanitize_value(item) for item in value]
    return value
