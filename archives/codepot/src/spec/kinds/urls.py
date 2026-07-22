"""Compiled spec URL kind enums."""

from __future__ import annotations

from enum import StrEnum


class UrlEnv(StrEnum):
    """Known URL environments."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    PREVIEW = "preview"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class UrlKind(StrEnum):
    """Known URL use/kind values."""

    API = "api"
    WEBSITE = "website"
    ADMIN = "admin"
    DOCS = "docs"
    ASSETS = "assets"
    CDN = "cdn"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    AUTH = "auth"
    CUSTOM = "custom"


class UrlProtocol(StrEnum):
    """Known URL protocol values."""

    HTTP = "http"
    HTTPS = "https"
    WS = "ws"
    WSS = "wss"
