from importlib import import_module
from typing import Any
_CANONICAL = import_module("dryv.ir.model.validation")
__all__ = tuple(getattr(_CANONICAL, "__all__", ()))
def __getattr__(name: str) -> Any: return getattr(_CANONICAL, name)
def __dir__() -> list[str]: return sorted(set(globals()) | set(__all__))
