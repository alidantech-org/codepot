"""Independent Jinja Render Client for the Dryv Render Session protocol."""

from .session import (
    CONTEXT_VERSION,
    JinjaRenderSession,
    PACKAGE_VERSION,
    RENDERER_CAPABILITY,
    RENDER_PROTOCOL_VERSION,
    RenderDiagnosticMessage,
    RenderResultMessage,
    RenderedOutputMessage,
    RendererHelloMessage,
    TEMPLATE_MEDIA_TYPES,
)

__version__ = PACKAGE_VERSION

__all__ = [
    "CONTEXT_VERSION",
    "JinjaRenderSession",
    "PACKAGE_VERSION",
    "RENDERER_CAPABILITY",
    "RENDER_PROTOCOL_VERSION",
    "RenderDiagnosticMessage",
    "RenderResultMessage",
    "RenderedOutputMessage",
    "RendererHelloMessage",
    "TEMPLATE_MEDIA_TYPES",
    "__version__",
]
