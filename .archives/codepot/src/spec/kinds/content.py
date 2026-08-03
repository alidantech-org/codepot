"""Compiled spec content kind enums."""

from __future__ import annotations

from enum import StrEnum


class ContentStrategy(StrEnum):
    """Supported content serialization strategies."""

    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    HTML = "html"
    CSV = "csv"
    MULTIPART = "multipart"
    FORM = "form"
    TEXT = "text"
    BINARY = "binary"
    STREAM = "stream"
    GRAPHQL = "graphql"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    CUSTOM = "custom"
