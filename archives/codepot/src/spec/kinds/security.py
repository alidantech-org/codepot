"""Compiled spec security kind enums."""

from __future__ import annotations

from enum import StrEnum


class SecurityCredentialSource(StrEnum):
    """Supported credential locations."""

    HEADER = "header"
    COOKIE = "cookie"
    QUERY = "query"


class SecurityCredentialFormat(StrEnum):
    """Supported credential formats."""

    RAW = "raw"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    SESSION = "session"


class SecurityPolicyMode(StrEnum):
    """Supported security policy modes."""

    PUBLIC = "public"
    PROTECTED = "protected"
