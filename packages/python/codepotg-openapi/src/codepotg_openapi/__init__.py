from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .options import OpenApiOptions
from .plugin import create_plugin
from .version import PACKAGE_VERSION as __version__

if TYPE_CHECKING:
    from .adapter import OpenApiSourceAdapter

__all__ = ["OpenApiOptions", "OpenApiSourceAdapter", "__version__", "create_plugin"]


def __getattr__(name: str) -> Any:
    if name == "OpenApiSourceAdapter":
        from .adapter import OpenApiSourceAdapter

        return OpenApiSourceAdapter
    raise AttributeError(name)
