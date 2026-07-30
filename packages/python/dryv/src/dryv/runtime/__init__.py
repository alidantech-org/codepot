from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from .plugins import PluginLoadError, RuntimePlugins

_LAZY_EXPORTS = {
    "DryvRuntime": ("dryv.runtime.facade", "DryvRuntime"),
    "RuntimePluginInfo": ("dryv.runtime.models", "RuntimePluginInfo"),
    "RuntimeSnapshot": ("dryv.runtime.models", "RuntimeSnapshot"),
    "create_runtime": ("dryv.runtime.facade", "create_runtime"),
}

if TYPE_CHECKING:
    from .facade import DryvRuntime, create_runtime
    from .models import RuntimePluginInfo, RuntimeSnapshot


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "DryvRuntime",
    "PluginLoadError",
    "RuntimePluginInfo",
    "RuntimePlugins",
    "RuntimeSnapshot",
    "create_runtime",
]
