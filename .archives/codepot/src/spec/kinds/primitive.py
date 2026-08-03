"""Compiled spec primitive kind enums."""

from __future__ import annotations

from enum import StrEnum


class PrimitiveType(StrEnum):
    """Supported primitive value types."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    INTEGER = "integer"


class PrimitiveFormat(StrEnum):
    """Supported primitive semantic formats."""

    DATE = "date"
    DATE_TIME = "date-time"
    TIME = "time"
    EMAIL = "email"
    URI = "uri"
    URL = "url"
    UUID = "uuid"
    OBJECT_ID = "object-id"
    PHONE = "phone"
    PASSWORD = "password"
    BINARY = "binary"
    CUSTOM = "custom"
