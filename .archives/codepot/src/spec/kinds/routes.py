"""Compiled spec route kind enums."""

from __future__ import annotations

from enum import StrEnum


class HttpMethod(StrEnum):
    """Supported HTTP methods."""

    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"
