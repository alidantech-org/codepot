"""TypeScript URL helper facts."""

from __future__ import annotations

from contracts.api import ApiContract

DEFAULT_BASE_URL = "https://api.example.com"


def default_base_url(api: ApiContract) -> str:
    """Return default base URL metadata for TypeScript templates."""
    servers = getattr(api, "servers", ())

    if isinstance(servers, tuple) and servers:
        first = servers[0]
        url = getattr(first, "url", None)
        if isinstance(url, str) and url.strip():
            return url.strip()

    return DEFAULT_BASE_URL
