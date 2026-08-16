"""Jinja Render Client for the renderer-neutral Dryv API protocol."""

from .client import JinjaRenderClient
from .renderer import PACKAGE_VERSION, RENDERER_CAPABILITY, RENDERER_ID, renderer_fingerprint

__version__ = PACKAGE_VERSION

__all__ = ["JinjaRenderClient", "PACKAGE_VERSION", "RENDERER_CAPABILITY", "RENDERER_ID", "renderer_fingerprint"]
