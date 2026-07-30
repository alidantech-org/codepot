from __future__ import annotations

from .engine import JinjaTemplateEngine


def create_plugin() -> JinjaTemplateEngine:
    """Create one strict engine instance without scanning or global registration."""

    return JinjaTemplateEngine()
