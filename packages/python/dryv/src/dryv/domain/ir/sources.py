from importlib import import_module
from typing import Any
_CANONICAL = import_module("dryv.ir.model.sources")
__all__ = tuple(name for name in dir(_CANONICAL) if not name.startswith("_"))
def __getattr__(name: str) -> Any: return getattr(_CANONICAL, name)
def __dir__() -> list[str]: return sorted(set(globals()) | set(__all__))
